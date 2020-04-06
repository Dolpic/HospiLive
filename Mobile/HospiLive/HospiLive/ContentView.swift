//
//  ContentView.swift
//  HospiLive
//
//  Created by ouelid chennoufi on 04/04/2020.
//  Copyright © 2020 NOL. All rights reserved.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        WebView(url: "https://lauzhack.sysmic.ch:8080")
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
