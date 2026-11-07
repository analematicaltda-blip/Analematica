import Foundation
#if canImport(UIKit)
import UIKit
#endif
public enum ScreenProtectionError: Error { case unavailable }

/// Public APIs only; cannot prevent every screenshot or an external camera.
public final class AppleSensitiveScreen {
    #if canImport(UIKit)
    @MainActor private final class Cover {
        weak var window: UIWindow?
        let view=UIView()
        init(_ window: UIWindow) { self.window=window; view.backgroundColor = .black; view.isAccessibilityElement=true; view.accessibilityLabel="Contenido protegido" }
    }
    @MainActor private static var inactive=false
    @MainActor private static var inactiveScenes=Set<ObjectIdentifier>()
    @MainActor private static var covers=[Cover]()
    @MainActor private static var observers=[NSObjectProtocol]()
    @MainActor private static func refresh() {
        covers=covers.filter { $0.window != nil }
        let windows=UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }.flatMap { $0.windows }
        for window in windows where !covers.contains(where: { $0.window === window }) { covers.append(Cover(window)) }
        for cover in covers {
            guard let window=cover.window else { continue }
            let sceneBlocked=window.windowScene.map { $0.activationState != .foregroundActive || inactiveScenes.contains(ObjectIdentifier($0)) } ?? true
            if inactive || sceneBlocked || UIApplication.shared.applicationState != .active || window.screen.isCaptured {
                cover.view.frame=window.bounds; cover.view.autoresizingMask=[.flexibleWidth,.flexibleHeight]
                window.addSubview(cover.view); window.bringSubviewToFront(cover.view)
            } else { cover.view.removeFromSuperview() }
        }
    }
    @MainActor private static func prepare() -> Bool {
        if observers.isEmpty {
            for name in [UIApplication.willResignActiveNotification, UIApplication.didBecomeActiveNotification, UIScreen.capturedDidChangeNotification, UIScene.willDeactivateNotification, UIScene.didActivateNotification] {
                observers.append(NotificationCenter.default.addObserver(forName: name, object: nil, queue: .main) { note in
                    MainActor.assumeIsolated {
                        if note.name == UIApplication.willResignActiveNotification { inactive=true }
                        if note.name == UIApplication.didBecomeActiveNotification { inactive=false }
                        if let scene=note.object as? UIScene {
                            if note.name == UIScene.willDeactivateNotification { inactiveScenes.insert(ObjectIdentifier(scene)) }
                            if note.name == UIScene.didActivateNotification { inactiveScenes.remove(ObjectIdentifier(scene)) }
                        }
                        refresh()
                    }
                })
            }
        }
        refresh()
        let windows=UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }.flatMap { $0.windows }.filter { $0.isKeyWindow && $0.windowScene?.activationState == .foregroundActive }
        return !inactive && UIApplication.shared.applicationState == .active && !windows.isEmpty && !windows.contains { $0.screen.isCaptured }
    }
    #endif
    public static func requireSensitiveDisplay() throws {
        #if canImport(UIKit)
        let allowed: Bool
        if Thread.isMainThread { allowed=MainActor.assumeIsolated { prepare() } }
        else { allowed=DispatchQueue.main.sync { MainActor.assumeIsolated { prepare() } } }
        guard allowed else { throw ScreenProtectionError.unavailable }
        #else
        throw ScreenProtectionError.unavailable
        #endif
    }
}
