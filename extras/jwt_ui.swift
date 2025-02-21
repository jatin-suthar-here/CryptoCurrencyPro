import SwiftUI

class AuthManager: ObservableObject {
    @Published var accessToken: String?
    @Published var refreshToken: String?
    
    let baseURL = "https://your-api.com"




    func saveTokens(access: String, refresh: String) {
        let keychain = KeychainSwift()
        keychain.set(access, forKey: "accessToken")
        keychain.set(refresh, forKey: "refreshToken")
        self.accessToken = access
        self.refreshToken = refresh
    }




    func login(username: String, password: String) {
        guard let url = URL(string: "\(baseURL)/login") else { return }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.httpBody = "username=\(username)&password=\(password)".data(using: .utf8)
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        URLSession.shared.dataTask(with: request) { data, response, _ in
            if let data = data, 
               let json = try? JSONSerialization.jsonObject(with: data) as? [String: String],
               let access = json["access_token"], let refresh = json["refresh_token"] {
                DispatchQueue.main.async {
                    self.saveTokens(access: access, refresh: refresh)
                }
            }
        }.resume()
    }


    func refreshAccessToken(completion: @escaping (Bool) -> Void) {
        guard let refreshToken = KeychainSwift().get("refreshToken"),
              let url = URL(string: "\(baseURL)/refresh") else {
            completion(false)
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.httpBody = "refresh_token=\(refreshToken)".data(using: .utf8)
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")

        URLSession.shared.dataTask(with: request) { data, response, _ in
            if let data = data,
               let json = try? JSONSerialization.jsonObject(with: data) as? [String: String],
               let newAccessToken = json["access_token"] {
                DispatchQueue.main.async {
                    self.accessToken = newAccessToken
                    KeychainSwift().set(newAccessToken, forKey: "accessToken")
                    completion(true)
                }
            } else {
                completion(false)
            }
        }.resume()
    }


    func fetchProtectedData() {
        guard let token = KeychainSwift().get("accessToken"), let url = URL(string: "\(baseURL)/protected") else { return }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.addValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        URLSession.shared.dataTask(with: request) { data, response, _ in
            if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 401 {
                // Token expired, refresh it
                self.refreshAccessToken { success in
                    if success { self.fetchProtectedData() }
                }
            } else if let data = data {
                let responseString = String(data: data, encoding: .utf8)
                print("Protected data: \(responseString ?? "")")
            }
        }.resume()
    }
}



