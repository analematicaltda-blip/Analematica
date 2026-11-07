// swift-tools-version: 5.9
import PackageDescription
let package = Package(name: "SGAApproval", platforms: [.iOS(.v15), .macOS(.v13)], products: [.library(name: "SGAApproval", targets: ["SGAApproval"])], targets: [.target(name: "SGAApproval"), .testTarget(name: "SGAApprovalTests", dependencies: ["SGAApproval"])])
