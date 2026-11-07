import Foundation
import Security

/// Dedicated ephemeral JSON client. No redirects, cookie persistence or disk cache.
public final class PinnedHTTPSClient {
    private let policy: OriginPinPolicy
    public init(policy: OriginPinPolicy) { self.policy=policy }
    public static func fromApplication() throws -> PinnedHTTPSClient {
        guard let config=Bundle.main.object(forInfoDictionaryKey: "SGACDNetwork") as? [String:String],
              let host=config["Host"], let raw=config["Pins"], let expiry=config["ValidUntil"],
              let timestamp=Int64(expiry), String(timestamp) == expiry,
              let url=URL(string: "https://"+host+"/") else { throw NetworkProtectionError.configurationRequired }
        let policy=try OriginPinPolicy(host: host, pins: Set(raw.components(separatedBy: ",")), validUntil: timestamp)
        try policy.requireOrigin(url); return PinnedHTTPSClient(policy: policy)
    }
    public func request(_ url: URL, json: Data? = nil, bearer: String? = nil, completion: @escaping (Result<Data,Error>) -> Void) {
        do {
            try policy.requireOrigin(url)
            guard (json?.count ?? 0) <= 65536 else { throw NetworkProtectionError.rejected }
            if let token=bearer { guard !token.isEmpty, token.count <= 4096, token.utf8.allSatisfy({ $0 > 32 && $0 < 127 }), token.range(of: "^[A-Za-z0-9._~+/-]+=*$",options: .regularExpression) != nil else { throw NetworkProtectionError.rejected } }
            let worker=PinnedRequest(policy: policy, completion: completion)
            worker.start(url, json: json, bearer: bearer)
        } catch { completion(.failure(NetworkProtectionError.rejected)) }
    }
}

private final class PinnedRequest: NSObject, URLSessionDataDelegate, URLSessionTaskDelegate {
    private let policy: OriginPinPolicy
    private var completion: ((Result<Data,Error>) -> Void)?
    private var bytes=Data()
    private var session: URLSession?
    init(policy: OriginPinPolicy, completion: @escaping (Result<Data,Error>) -> Void) { self.policy=policy; self.completion=completion }
    func start(_ url: URL, json: Data?, bearer: String?) {
        let config=URLSessionConfiguration.ephemeral
        config.urlCache=nil; config.httpCookieStorage=nil; config.httpShouldSetCookies=false; config.urlCredentialStorage=nil
        config.requestCachePolicy = .reloadIgnoringLocalCacheData; config.timeoutIntervalForRequest=10; config.timeoutIntervalForResource=30
        config.tlsMinimumSupportedProtocolVersion = .TLSv12
        let queue=OperationQueue(); queue.maxConcurrentOperationCount=1
        let session=URLSession(configuration: config, delegate: self, delegateQueue: queue); self.session=session
        var request=URLRequest(url: url); request.httpMethod=json == nil ? "GET" : "POST"; request.httpBody=json
        request.setValue("application/json", forHTTPHeaderField: "Accept"); request.setValue("no-store", forHTTPHeaderField: "Cache-Control")
        if json != nil { request.setValue("application/json", forHTTPHeaderField: "Content-Type") }
        if let bearer { request.setValue("Bearer "+bearer, forHTTPHeaderField: "Authorization") }
        session.dataTask(with: request).resume()
    }
    private func finish(_ result: Result<Data,Error>) {
        guard let callback=completion else { return }; completion=nil
        session?.invalidateAndCancel(); session=nil; bytes.resetBytes(in: 0..<bytes.count); callback(result)
    }
    func urlSession(_ session: URLSession, task: URLSessionTask, willPerformHTTPRedirection response: HTTPURLResponse, newRequest request: URLRequest, completionHandler: @escaping (URLRequest?) -> Void) {
        completionHandler(nil); finish(.failure(NetworkProtectionError.rejected))
    }
    func urlSession(_ session: URLSession, dataTask: URLSessionDataTask, didReceive response: URLResponse, completionHandler: @escaping (URLSession.ResponseDisposition) -> Void) {
        do {
            guard let response=response as? HTTPURLResponse, let url=response.url, (200..<300).contains(response.statusCode), response.expectedContentLength <= 1048576 else { throw NetworkProtectionError.rejected }
            try policy.requireOrigin(url); completionHandler(.allow)
        } catch { completionHandler(.cancel); finish(.failure(NetworkProtectionError.rejected)) }
    }
    func urlSession(_ session: URLSession, dataTask: URLSessionDataTask, didReceive data: Data) {
        guard completion != nil, bytes.count+data.count <= 1048576 else { finish(.failure(NetworkProtectionError.rejected)); return }; bytes.append(data)
    }
    func urlSession(_ session: URLSession, task: URLSessionTask, didCompleteWithError error: Error?) {
        do {
            guard error == nil, let url=task.originalRequest?.url else { throw NetworkProtectionError.rejected }
            try policy.requireOrigin(url); finish(.success(bytes))
        } catch { finish(.failure(NetworkProtectionError.rejected)) }
    }
    func urlSession(_ session: URLSession, didReceive challenge: URLAuthenticationChallenge, completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        do {
            guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
                  challenge.protectionSpace.port == 443,
                  let origin=URL(string: "https://"+challenge.protectionSpace.host), let trust=challenge.protectionSpace.serverTrust else { throw NetworkProtectionError.rejected }
            try policy.requireOrigin(origin)
            let ssl=SecPolicyCreateSSL(true,challenge.protectionSpace.host as CFString)
            guard SecTrustSetPolicies(trust,ssl) == errSecSuccess, SecTrustEvaluateWithError(trust,nil) else { throw NetworkProtectionError.rejected }
            let count=SecTrustGetCertificateCount(trust); guard count > 0 && count <= 10 else { throw NetworkProtectionError.rejected }
            for index in 0..<count {
                if let cert=SecTrustGetCertificateAtIndex(trust,index), let key=SecCertificateCopyKey(cert), let spki=SPKIEncoding.encode(key), try policy.acceptsSPKI(spki) {
                    completionHandler(.useCredential,URLCredential(trust: trust)); return
                }
            }
        } catch { /* No trust fallback. */ }
        completionHandler(.cancelAuthenticationChallenge,nil)
    }
}

// Internal for independent cross-platform SPKI vectors in tests.
enum SPKIEncoding {
    // SecKey external representation is NOT SPKI. Wrap PKCS#1 RSA or X9.62 P-256
    // with its ASN.1 AlgorithmIdentifier before computing cross-platform pins.
    private static func der(_ tag: UInt8,_ value: Data) -> Data {
        let n=value.count
        let length: [UInt8]=n < 128 ? [UInt8(n)] : n < 256 ? [0x81,UInt8(n)] : [0x82,UInt8(n >> 8),UInt8(n & 255)]
        return Data([tag]+length)+value
    }
    static func encode(_ key: SecKey) -> Data? {
        guard let attrs=SecKeyCopyAttributes(key) as? [String:Any], let encoded=SecKeyCopyExternalRepresentation(key,nil) else { return nil }
        let raw=encoded as Data
        guard raw.count <= 16384 else { return nil }
        let algorithm: Data
        if attrs[kSecAttrKeyType as String] as? String == kSecAttrKeyTypeRSA as String {
            algorithm=Data([0x30,0x0d,0x06,0x09,0x2a,0x86,0x48,0x86,0xf7,0x0d,0x01,0x01,0x01,0x05,0x00])
        } else if attrs[kSecAttrKeyType as String] as? String == kSecAttrKeyTypeECSECPrimeRandom as String, attrs[kSecAttrKeySizeInBits as String] as? Int == 256, raw.count == 65, raw.first == 4 {
            algorithm=Data([0x30,0x13,0x06,0x07,0x2a,0x86,0x48,0xce,0x3d,0x02,0x01,0x06,0x08,0x2a,0x86,0x48,0xce,0x3d,0x03,0x01,0x07])
        } else { return nil }
        return der(0x30,algorithm+der(0x03,Data([0])+raw))
    }
}
