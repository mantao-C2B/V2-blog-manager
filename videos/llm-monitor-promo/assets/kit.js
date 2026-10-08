/* LLM Monitor video kit — shared helpers for every scene.
   Loaded once by index.html; sub-compositions call window.LM.*.
   Deterministic only: no clocks, no Math.random, no network. */
(function () {
  const ICONS = {"search": "<path d=\"m21 21-4.34-4.34\" /> <circle cx=\"11\" cy=\"11\" r=\"8\" />", "arrow-up": "<path d=\"m5 12 7-7 7 7\" /> <path d=\"M12 19V5\" />", "arrow-right": "<path d=\"M5 12h14\" /> <path d=\"m12 5 7 7-7 7\" />", "sparkles": "<path d=\"M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z\" /> <path d=\"M20 2v4\" /> <path d=\"M22 4h-4\" /> <circle cx=\"4\" cy=\"20\" r=\"2\" />", "users": "<path d=\"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2\" /> <path d=\"M16 3.128a4 4 0 0 1 0 7.744\" /> <path d=\"M22 21v-2a4 4 0 0 0-3-3.87\" /> <circle cx=\"9\" cy=\"7\" r=\"4\" />", "repeat": "<path d=\"m17 2 4 4-4 4\" /> <path d=\"M3 11v-1a4 4 0 0 1 4-4h14\" /> <path d=\"m7 22-4-4 4-4\" /> <path d=\"M21 13v1a4 4 0 0 1-4 4H3\" />", "bell": "<path d=\"M10.268 21a2 2 0 0 0 3.464 0\" /> <path d=\"M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326\" />", "trending-up": "<path d=\"M16 7h6v6\" /> <path d=\"m22 7-8.5 8.5-5-5L2 17\" />", "trending-down": "<path d=\"M16 17h6v-6\" /> <path d=\"m22 17-8.5-8.5-5 5L2 7\" />", "triangle-alert": "<path d=\"m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3\" /> <path d=\"M12 9v4\" /> <path d=\"M12 17h.01\" />", "check": "<path d=\"M20 6 9 17l-5-5\" />", "x": "<path d=\"M18 6 6 18\" /> <path d=\"m6 6 12 12\" />", "globe": "<circle cx=\"12\" cy=\"12\" r=\"10\" /> <path d=\"M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20\" /> <path d=\"M2 12h20\" />", "message-square": "<path d=\"M22 17a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 21.286V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z\" />", "newspaper": "<path d=\"M15 18h-5\" /> <path d=\"M18 14h-8\" /> <path d=\"M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-4 0v-9a2 2 0 0 1 2-2h2\" /> <rect width=\"8\" height=\"4\" x=\"10\" y=\"6\" rx=\"1\" />", "star": "<path d=\"M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z\" />", "shield-check": "<path d=\"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z\" /> <path d=\"m9 12 2 2 4-4\" />", "mouse-pointer-2": "<path d=\"M4.037 4.688a.495.495 0 0 1 .651-.651l16 6.5a.5.5 0 0 1-.063.947l-6.124 1.58a2 2 0 0 0-1.438 1.435l-1.579 6.126a.5.5 0 0 1-.947.063z\" />", "zap": "<path d=\"M15.914 4a1.5 1.5 0 00-2.474-1.561l-9 9A1.5 1.5 0 005.5 14h4.002a.5.5 0 01.471.666L8.086 20a1.5 1.5 0 002.475 1.56l9-9A1.5 1.5 0 0018.5 10h-3.997a.5.5 0 01-.472-.667z\" />", "chart-column": "<path d=\"M3 3v16a2 2 0 0 0 2 2h16\" /> <path d=\"M18 17V9\" /> <path d=\"M13 17V5\" /> <path d=\"M8 17v-3\" />", "messages-square": "<path d=\"M16 10a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 14.286V4a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z\" /> <path d=\"M20 9a2 2 0 0 1 2 2v10.286a.71.71 0 0 1-1.212.502l-2.202-2.202A2 2 0 0 0 17.172 19H10a2 2 0 0 1-2-2v-1\" />", "user": "<path d=\"M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2\" /> <circle cx=\"12\" cy=\"7\" r=\"4\" />", "refresh-cw": "<path d=\"M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8\" /> <path d=\"M21 3v5h-5\" /> <path d=\"M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16\" /> <path d=\"M8 16H3v5\" />", "circle-check": "<circle cx=\"12\" cy=\"12\" r=\"10\" /> <path d=\"m16 9-5.5 5.5L8 12\" />", "circle-x": "<circle cx=\"12\" cy=\"12\" r=\"10\" /> <path d=\"m15 9-6 6\" /> <path d=\"m9 9 6 6\" />", "circle-alert": "<circle cx=\"12\" cy=\"12\" r=\"10\" /> <line x1=\"12\" x2=\"12\" y1=\"8\" y2=\"12\" /> <line x1=\"12\" x2=\"12.01\" y1=\"16\" y2=\"16\" />", "thumbs-up": "<path d=\"M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88Z\" /> <path d=\"M7 10v12\" />", "thumbs-down": "<path d=\"M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22a3.13 3.13 0 0 1-3-3.88Z\" /> <path d=\"M17 14V2\" />", "link": "<path d=\"M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71\" /> <path d=\"M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71\" />", "file-text": "<path d=\"M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z\" /> <path d=\"M14 2v5a1 1 0 0 0 1 1h5\" /> <path d=\"M10 9H8\" /> <path d=\"M16 13H8\" /> <path d=\"M16 17H8\" />", "store": "<path d=\"M15 21v-5a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v5\" /> <path d=\"M17.774 10.31a1.12 1.12 0 0 0-1.549 0 2.5 2.5 0 0 1-3.451 0 1.12 1.12 0 0 0-1.548 0 2.5 2.5 0 0 1-3.452 0 1.12 1.12 0 0 0-1.549 0 2.5 2.5 0 0 1-3.77-3.248l2.889-4.184A2 2 0 0 1 7 2h10a2 2 0 0 1 1.653.873l2.895 4.192a2.5 2.5 0 0 1-3.774 3.244\" /> <path d=\"M4 10.95V19a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8.05\" />", "megaphone": "<path d=\"M11 6a13 13 0 0 0 8.4-2.8A1 1 0 0 1 21 4v12a1 1 0 0 1-1.6.8A13 13 0 0 0 11 14H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2z\" /> <path d=\"M6 14a12 12 0 0 0 2.4 7.2 2 2 0 0 0 3.2-2.4A8 8 0 0 1 10 14\" /> <path d=\"M8 6v8\" />", "eye": "<path d=\"M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0\" /> <circle cx=\"12\" cy=\"12\" r=\"3\" />", "radar": "<path d=\"M19.07 4.93A10 10 0 0 0 6.99 3.34\" /> <path d=\"M4 6h.01\" /> <path d=\"M2.29 9.62A10 10 0 1 0 21.31 8.35\" /> <path d=\"M16.24 7.76A6 6 0 1 0 8.23 16.67\" /> <path d=\"M12 18h.01\" /> <path d=\"M17.99 11.66A6 6 0 0 1 15.77 16.67\" /> <circle cx=\"12\" cy=\"12\" r=\"2\" /> <path d=\"m13.41 10.59 5.66-5.66\" />", "activity": "<path d=\"M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2\" />", "target": "<circle cx=\"12\" cy=\"12\" r=\"10\" /> <circle cx=\"12\" cy=\"12\" r=\"6\" /> <circle cx=\"12\" cy=\"12\" r=\"2\" />", "play": "<path d=\"M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z\" />", "smile": "<path d=\"M15 10V9\" /> <path d=\"M16.472 15a6 6 0 01-8.943 0\" /> <path d=\"M9 10V9\" /> <circle cx=\"12\" cy=\"12\" r=\"10\" />", "chevron-right": "<path d=\"m9 18 6-6-6-6\" />", "plus": "<path d=\"M5 12h14\" /> <path d=\"M12 5v14\" />", "minus": "<path d=\"M5 12h14\" />", "shopping-bag": "<path d=\"M16 10a4 4 0 0 1-8 0\" /> <path d=\"M3.103 6.034h17.794\" /> <path d=\"M3.4 5.467a2 2 0 0 0-.4 1.2V20a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6.667a2 2 0 0 0-.4-1.2l-2-2.667A2 2 0 0 0 17 2H7a2 2 0 0 0-1.6.8z\" />", "award": "<path d=\"m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.197 0l-3.586 2.686a.5.5 0 0 1-.81-.469l1.514-8.526\" /> <circle cx=\"12\" cy=\"8\" r=\"6\" />", "book-open": "<path d=\"M12 5v16\" /> <path d=\"M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2H4a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z\" />", "scan-search": "<path d=\"M3 7V5a2 2 0 0 1 2-2h2\" /> <path d=\"M17 3h2a2 2 0 0 1 2 2v2\" /> <path d=\"M21 17v2a2 2 0 0 1-2 2h-2\" /> <path d=\"M7 21H5a2 2 0 0 1-2-2v-2\" /> <circle cx=\"12\" cy=\"12\" r=\"3\" /> <path d=\"m16 16-1.9-1.9\" />", "file-code": "<path d=\"M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z\" /> <path d=\"M14 2v5a1 1 0 0 0 1 1h5\" /> <path d=\"M10 12.5 8 15l2 2.5\" /> <path d=\"m14 12.5 2 2.5-2 2.5\" />", "bot": "<path d=\"M12 8V4H8\" /> <rect width=\"16\" height=\"12\" x=\"4\" y=\"8\" rx=\"2\" /> <path d=\"M2 14h2\" /> <path d=\"M20 14h2\" /> <path d=\"M15 13v2\" /> <path d=\"M9 13v2\" />", "network": "<rect x=\"16\" y=\"16\" width=\"6\" height=\"6\" rx=\"1\" /> <rect x=\"2\" y=\"16\" width=\"6\" height=\"6\" rx=\"1\" /> <rect x=\"9\" y=\"2\" width=\"6\" height=\"6\" rx=\"1\" /> <path d=\"M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3\" /> <path d=\"M12 12V8\" />", "list-checks": "<path d=\"M13 5h8\" /> <path d=\"M13 12h8\" /> <path d=\"M13 19h8\" /> <path d=\"m3 17 2 2 4-4\" /> <path d=\"m3 7 2 2 4-4\" />", "gauge": "<path d=\"m12 14 4-4\" /> <path d=\"M3.34 19a10 10 0 1 1 17.32 0\" />", "rotate-cw": "<path d=\"M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8\" /> <path d=\"M21 3v5h-5\" />", "lock": "<rect width=\"18\" height=\"11\" x=\"3\" y=\"11\" rx=\"2\" ry=\"2\" /> <path d=\"M7 11V7a5 5 0 0 1 10 0v4\" />", "layout-list": "<rect width=\"7\" height=\"7\" x=\"3\" y=\"3\" rx=\"1\" /> <rect width=\"7\" height=\"7\" x=\"3\" y=\"14\" rx=\"1\" /> <path d=\"M14 4h7\" /> <path d=\"M14 9h7\" /> <path d=\"M14 15h7\" /> <path d=\"M14 20h7\" />", "heading": "<path d=\"M6 12h12\" /> <path d=\"M6 20V4\" /> <path d=\"M18 20V4\" />", "table": "<path d=\"M12 3v18\" /> <rect width=\"18\" height=\"18\" x=\"3\" y=\"3\" rx=\"2\" /> <path d=\"M3 9h18\" /> <path d=\"M3 15h18\" />", "sparkle": "<path d=\"M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z\" />", "quote": "<path d=\"M16 3a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2 1 1 0 0 1 1 1v1a2 2 0 0 1-2 2 1 1 0 0 0-1 1v2a1 1 0 0 0 1 1 6 6 0 0 0 6-6V5a2 2 0 0 0-2-2z\" /> <path d=\"M5 3a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2 1 1 0 0 1 1 1v1a2 2 0 0 1-2 2 1 1 0 0 0-1 1v2a1 1 0 0 0 1 1 6 6 0 0 0 6-6V5a2 2 0 0 0-2-2z\" />", "footprints": "<path d=\"M4 16v-2.38C4 11.5 2.97 10.5 3 8c.03-2.72 1.49-6 4.5-6C9.37 2 10 3.8 10 5.5c0 3.11-2 5.66-2 8.68V16a2 2 0 1 1-4 0Z\" /> <path d=\"M20 20v-2.38c0-2.12 1.03-3.12 1-5.62-.03-2.72-1.49-6-4.5-6C14.63 6 14 7.8 14 9.5c0 3.11 2 5.66 2 8.68V20a2 2 0 1 0 4 0Z\" /> <path d=\"M16 17h4\" /> <path d=\"M4 13h4\" />", "briefcase": "<path d=\"M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16\" /> <rect width=\"20\" height=\"14\" x=\"2\" y=\"6\" rx=\"2\" />", "building-2": "<path d=\"M10 12h4\" /> <path d=\"M10 8h4\" /> <path d=\"M14 21v-3a2 2 0 0 0-4 0v3\" /> <path d=\"M6 10H4a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-2\" /> <path d=\"M6 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16\" />", "crosshair": "<circle cx=\"12\" cy=\"12\" r=\"10\" /> <line x1=\"22\" x2=\"18\" y1=\"12\" y2=\"12\" /> <line x1=\"6\" x2=\"2\" y1=\"12\" y2=\"12\" /> <line x1=\"12\" x2=\"12\" y1=\"6\" y2=\"2\" /> <line x1=\"12\" x2=\"12\" y1=\"22\" y2=\"18\" />", "loader": "<path d=\"M12 2v4\" /> <path d=\"m16.2 7.8 2.9-2.9\" /> <path d=\"M18 12h4\" /> <path d=\"m16.2 16.2 2.9 2.9\" /> <path d=\"M12 18v4\" /> <path d=\"m4.9 19.1 2.9-2.9\" /> <path d=\"M2 12h4\" /> <path d=\"m4.9 4.9 2.9 2.9\" />", "circle-dot": "<circle cx=\"12\" cy=\"12\" r=\"1\" /> <circle cx=\"12\" cy=\"12\" r=\"10\" />", "clock-arrow-up": "<path d=\"M12 6v6l1.56.78\" /> <path d=\"M13.227 21.925a10 10 0 1 1 8.767-9.588\" /> <path d=\"m14 18 4-4 4 4\" /> <path d=\"M18 22v-8\" />", "arrow-down-right": "<path d=\"m7 7 10 10\" /> <path d=\"M17 7v10H7\" />", "arrow-up-right": "<path d=\"M7 7h10v10\" /> <path d=\"M7 17 17 7\" />"};
  const LOGOS = {"google": "<svg width=\"100%\" height=\"100%\" viewBox=\"0 0 24 24\" xmlns=\"http://www.w3.org/2000/svg\"><path d=\"M23 12.245c0-.905-.075-1.565-.236-2.25h-10.54v4.083h6.186c-.124 1.014-.797 2.542-2.294 3.569l-.021.136 3.332 2.53.23.022C21.779 18.417 23 15.593 23 12.245z\" fill=\"#4285F4\"></path><path d=\"M12.225 23c3.03 0 5.574-.978 7.433-2.665l-3.542-2.688c-.948.648-2.22 1.1-3.891 1.1a6.745 6.745 0 01-6.386-4.572l-.132.011-3.465 2.628-.045.124C4.043 20.531 7.835 23 12.225 23z\" fill=\"#34A853\"></path><path d=\"M5.84 14.175A6.65 6.65 0 015.463 12c0-.758.138-1.491.361-2.175l-.006-.147-3.508-2.67-.115.054A10.831 10.831 0 001 12c0 1.772.436 3.447 1.197 4.938l3.642-2.763z\" fill=\"#FBBC05\"></path><path d=\"M12.225 5.253c2.108 0 3.529.892 4.34 1.638l3.167-3.031C17.787 2.088 15.255 1 12.225 1 7.834 1 4.043 3.469 2.197 7.062l3.63 2.763a6.77 6.77 0 016.398-4.572z\" fill=\"#EB4335\"></path></svg>", "chatgpt": "<svg width=\"100%\" height=\"100%\" fill=\"#0e1a17\" fill-rule=\"evenodd\" viewBox=\"0 0 24 24\" xmlns=\"http://www.w3.org/2000/svg\"><path d=\"M9.205 8.658v-2.26c0-.19.072-.333.238-.428l4.543-2.616c.619-.357 1.356-.523 2.117-.523 2.854 0 4.662 2.212 4.662 4.566 0 .167 0 .357-.024.547l-4.71-2.759a.797.797 0 00-.856 0l-5.97 3.473zm10.609 8.8V12.06c0-.333-.143-.57-.429-.737l-5.97-3.473 1.95-1.118a.433.433 0 01.476 0l4.543 2.617c1.309.76 2.189 2.378 2.189 3.948 0 1.808-1.07 3.473-2.76 4.163zM7.802 12.703l-1.95-1.142c-.167-.095-.239-.238-.239-.428V5.899c0-2.545 1.95-4.472 4.591-4.472 1 0 1.927.333 2.712.928L8.23 5.067c-.285.166-.428.404-.428.737v6.898zM12 15.128l-2.795-1.57v-3.33L12 8.658l2.795 1.57v3.33L12 15.128zm1.796 7.23c-1 0-1.927-.332-2.712-.927l4.686-2.712c.285-.166.428-.404.428-.737v-6.898l1.974 1.142c.167.095.238.238.238.428v5.233c0 2.545-1.974 4.472-4.614 4.472zm-5.637-5.303l-4.544-2.617c-1.308-.761-2.188-2.378-2.188-3.948A4.482 4.482 0 014.21 6.327v5.423c0 .333.143.571.428.738l5.947 3.449-1.95 1.118a.432.432 0 01-.476 0zm-.262 3.9c-2.688 0-4.662-2.021-4.662-4.519 0-.19.024-.38.047-.57l4.686 2.71c.286.167.571.167.856 0l5.97-3.448v2.26c0 .19-.07.333-.237.428l-4.543 2.616c-.619.357-1.356.523-2.117.523zm5.899 2.83a5.947 5.947 0 005.827-4.756C22.287 18.339 24 15.84 24 13.296c0-1.665-.713-3.282-1.998-4.448.119-.5.19-.999.19-1.498 0-3.401-2.759-5.947-5.946-5.947-.642 0-1.26.095-1.88.31A5.962 5.962 0 0010.205 0a5.947 5.947 0 00-5.827 4.757C1.713 5.447 0 7.945 0 10.49c0 1.666.713 3.283 1.998 4.448-.119.5-.19 1-.19 1.499 0 3.401 2.759 5.946 5.946 5.946.642 0 1.26-.095 1.88-.309a5.96 5.96 0 004.162 1.713z\"></path></svg>", "gemini": "<svg width=\"100%\" height=\"100%\" viewBox=\"0 0 24 24\" xmlns=\"http://www.w3.org/2000/svg\"><path d=\"M20.616 10.835a14.147 14.147 0 01-4.45-3.001 14.111 14.111 0 01-3.678-6.452.503.503 0 00-.975 0 14.134 14.134 0 01-3.679 6.452 14.155 14.155 0 01-4.45 3.001c-.65.28-1.318.505-2.002.678a.502.502 0 000 .975c.684.172 1.35.397 2.002.677a14.147 14.147 0 014.45 3.001 14.112 14.112 0 013.679 6.453.502.502 0 00.975 0c.172-.685.397-1.351.677-2.003a14.145 14.145 0 013.001-4.45 14.113 14.113 0 016.453-3.678.503.503 0 000-.975 13.245 13.245 0 01-2.003-.678z\" fill=\"#3186FF\"></path><path d=\"M20.616 10.835a14.147 14.147 0 01-4.45-3.001 14.111 14.111 0 01-3.678-6.452.503.503 0 00-.975 0 14.134 14.134 0 01-3.679 6.452 14.155 14.155 0 01-4.45 3.001c-.65.28-1.318.505-2.002.678a.502.502 0 000 .975c.684.172 1.35.397 2.002.677a14.147 14.147 0 014.45 3.001 14.112 14.112 0 013.679 6.453.502.502 0 00.975 0c.172-.685.397-1.351.677-2.003a14.145 14.145 0 013.001-4.45 14.113 14.113 0 016.453-3.678.503.503 0 000-.975 13.245 13.245 0 01-2.003-.678z\" fill=\"url(#lm-gemini-lobe-icons-gemini-0-_R_0_)\"></path><path d=\"M20.616 10.835a14.147 14.147 0 01-4.45-3.001 14.111 14.111 0 01-3.678-6.452.503.503 0 00-.975 0 14.134 14.134 0 01-3.679 6.452 14.155 14.155 0 01-4.45 3.001c-.65.28-1.318.505-2.002.678a.502.502 0 000 .975c.684.172 1.35.397 2.002.677a14.147 14.147 0 014.45 3.001 14.112 14.112 0 013.679 6.453.502.502 0 00.975 0c.172-.685.397-1.351.677-2.003a14.145 14.145 0 013.001-4.45 14.113 14.113 0 016.453-3.678.503.503 0 000-.975 13.245 13.245 0 01-2.003-.678z\" fill=\"url(#lm-gemini-lobe-icons-gemini-1-_R_0_)\"></path><path d=\"M20.616 10.835a14.147 14.147 0 01-4.45-3.001 14.111 14.111 0 01-3.678-6.452.503.503 0 00-.975 0 14.134 14.134 0 01-3.679 6.452 14.155 14.155 0 01-4.45 3.001c-.65.28-1.318.505-2.002.678a.502.502 0 000 .975c.684.172 1.35.397 2.002.677a14.147 14.147 0 014.45 3.001 14.112 14.112 0 013.679 6.453.502.502 0 00.975 0c.172-.685.397-1.351.677-2.003a14.145 14.145 0 013.001-4.45 14.113 14.113 0 016.453-3.678.503.503 0 000-.975 13.245 13.245 0 01-2.003-.678z\" fill=\"url(#lm-gemini-lobe-icons-gemini-2-_R_0_)\"></path><defs><linearGradient gradientUnits=\"userSpaceOnUse\" id=\"lm-gemini-lobe-icons-gemini-0-_R_0_\" x1=\"7\" x2=\"11\" y1=\"15.5\" y2=\"12\"><stop stop-color=\"#08B962\"></stop><stop offset=\"1\" stop-color=\"#08B962\" stop-opacity=\"0\"></stop></linearGradient><linearGradient gradientUnits=\"userSpaceOnUse\" id=\"lm-gemini-lobe-icons-gemini-1-_R_0_\" x1=\"8\" x2=\"11.5\" y1=\"5.5\" y2=\"11\"><stop stop-color=\"#F94543\"></stop><stop offset=\"1\" stop-color=\"#F94543\" stop-opacity=\"0\"></stop></linearGradient><linearGradient gradientUnits=\"userSpaceOnUse\" id=\"lm-gemini-lobe-icons-gemini-2-_R_0_\" x1=\"3.5\" x2=\"17.5\" y1=\"13.5\" y2=\"12\"><stop stop-color=\"#FABC12\"></stop><stop offset=\".46\" stop-color=\"#FABC12\" stop-opacity=\"0\"></stop></linearGradient></defs></svg>", "claude": "<svg width=\"100%\" height=\"100%\" viewBox=\"0 0 24 24\" xmlns=\"http://www.w3.org/2000/svg\"><path d=\"M4.709 15.955l4.72-2.647.08-.23-.08-.128H9.2l-.79-.048-2.698-.073-2.339-.097-2.266-.122-.571-.121L0 11.784l.055-.352.48-.321.686.06 1.52.103 2.278.158 1.652.097 2.449.255h.389l.055-.157-.134-.098-.103-.097-2.358-1.596-2.552-1.688-1.336-.972-.724-.491-.364-.462-.158-1.008.656-.722.881.06.225.061.893.686 1.908 1.476 2.491 1.833.365.304.145-.103.019-.073-.164-.274-1.355-2.446-1.446-2.49-.644-1.032-.17-.619a2.97 2.97 0 01-.104-.729L6.283.134 6.696 0l.996.134.42.364.62 1.414 1.002 2.229 1.555 3.03.456.898.243.832.091.255h.158V9.01l.128-1.706.237-2.095.23-2.695.08-.76.376-.91.747-.492.584.28.48.685-.067.444-.286 1.851-.559 2.903-.364 1.942h.212l.243-.242.985-1.306 1.652-2.064.73-.82.85-.904.547-.431h1.033l.76 1.129-.34 1.166-1.064 1.347-.881 1.142-1.264 1.7-.79 1.36.073.11.188-.02 2.856-.606 1.543-.28 1.841-.315.833.388.091.395-.328.807-1.969.486-2.309.462-3.439.813-.042.03.049.061 1.549.146.662.036h1.622l3.02.225.79.522.474.638-.079.485-1.215.62-1.64-.389-3.829-.91-1.312-.329h-.182v.11l1.093 1.068 2.006 1.81 2.509 2.33.127.578-.322.455-.34-.049-2.205-1.657-.851-.747-1.926-1.62h-.128v.17l.444.649 2.345 3.521.122 1.08-.17.353-.608.213-.668-.122-1.374-1.925-1.415-2.167-1.143-1.943-.14.08-.674 7.254-.316.37-.729.28-.607-.461-.322-.747.322-1.476.389-1.924.315-1.53.286-1.9.17-.632-.012-.042-.14.018-1.434 1.967-2.18 2.945-1.726 1.845-.414.164-.717-.37.067-.662.401-.589 2.388-3.036 1.44-1.882.93-1.086-.006-.158h-.055L4.132 18.56l-1.13.146-.487-.456.061-.746.231-.243 1.908-1.312-.006.006z\" fill=\"#D97757\" fill-rule=\"nonzero\"></path></svg>", "perplexity": "<svg width=\"100%\" height=\"100%\" viewBox=\"0 0 24 24\" xmlns=\"http://www.w3.org/2000/svg\"><path d=\"M19.785 0v7.272H22.5V17.62h-2.935V24l-7.037-6.194v6.145h-1.091v-6.152L4.392 24v-6.465H1.5V7.188h2.884V0l7.053 6.494V.19h1.09v6.49L19.786 0zm-7.257 9.044v7.319l5.946 5.234V14.44l-5.946-5.397zm-1.099-.08l-5.946 5.398v7.235l5.946-5.234V8.965zm8.136 7.58h1.844V8.349H13.46l6.105 5.54v2.655zm-8.982-8.28H2.59v8.195h1.8v-2.576l6.192-5.62zM5.475 2.476v4.71h5.115l-5.115-4.71zm13.219 0l-5.115 4.71h5.115v-4.71z\" fill=\"#22B8CD\" fill-rule=\"nonzero\"></path></svg>"};

  const C = {
    ink: "#0e1a17", green: "#117d67", mint: "#2ebe9b", white: "#ffffff",
    sable: "#eceeeb", canvas: "#f5f6f3", line: "#e1e5e0", inkSoft: "#4e5a56",
    inkFaint: "#8b9692", mintSoft: "#e4f3ee", navy900: "#15223a", navy800: "#1e3149",
    teal600: "#3f7f76", coral: "#d9785f", coralSoft: "#fbeae5",
  };

  function icon(name, opts) {
    const o = opts || {};
    const body = ICONS[name];
    if (!body) return "";
    const stroke = o.stroke || "currentColor";
    const sw = o.strokeWidth == null ? 2 : o.strokeWidth;
    const fill = o.fill || "none";
    return (
      '<svg viewBox="0 0 24 24" fill="' + fill + '" stroke="' + stroke + '" stroke-width="' + sw +
      '" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">' + body + "</svg>"
    );
  }

  function logo(name) {
    return LOGOS[name] || "";
  }

  /* ---------- Official LLM Monitor symbol (Guide logo v1.0, viewBox 0 0 100 100) ----------
     Visible extent of the drawn symbol = 74.06 % of the box (dash gaps sit on the tips),
     so a symbol of visible height X needs a box of X / 0.7406. */
  const SYM_VISIBLE = 0.7406;
  const SYM_PERIOD = 56.485;
  function symbol(o) {
    const opt = o || {};
    const color = opt.color || C.green;
    const size = opt.size || 100;
    const id = opt.id ? ' id="' + opt.id + '"' : "";
    return (
      '<svg' + id + ' class="lm-sym ' + (opt.cls || "") + '" viewBox="0 0 100 100" width="' + size + '" height="' + size +
      '" fill="none" xmlns="http://www.w3.org/2000/svg" style="overflow:visible;color:' + color + '">' +
      '<g class="lm-sym-ring" style="transform-origin:50px 50px;transform-box:view-box">' +
      '<rect class="lm-sym-rect" x="20" y="20" width="60" height="60" rx="8" transform="rotate(45 50 50)" stroke="currentColor"' +
      ' stroke-width="' + (opt.stroke || 7.2) + '" stroke-linecap="round" stroke-dasharray="34.6 21.885" stroke-dashoffset="-4.7"/>' +
      "</g>" +
      '<circle class="lm-sym-dot" cx="50" cy="50" r="10.6" fill="currentColor" style="transform-origin:50px 50px;transform-box:view-box"/>' +
      "</svg>"
    );
  }

  /* Horizontal lockup. X = visible symbol height in px. Cap height of the name = 0.58 X,
     visible gap symbol → name ≈ 0.5 X (measured on the guide). theme: "light" | "dark". */
  function lockup(X, theme, o) {
    const opt = o || {};
    const dark = theme === "dark";
    const picto = dark ? C.mint : C.green;
    const name = dark ? C.white : C.ink;
    const box = X / SYM_VISIBLE;
    const margin = (box - X) / 2;
    const fontSize = (0.58 * X) / 0.73;
    return (
      '<div class="lm-lockup ' + (opt.cls || "") + '"' + (opt.id ? ' id="' + opt.id + '"' : "") + ">" +
      '<span class="lm-lockup-sym" style="display:block;width:' + box.toFixed(2) + "px;height:" + box.toFixed(2) +
      "px;margin:-" + margin.toFixed(2) + "px -" + margin.toFixed(2) + 'px">' +
      symbol({ color: picto, size: box.toFixed(2) }) + "</span>" +
      '<span class="lm-lockup-name" style="display:block;color:' + name + ";font-size:" + fontSize.toFixed(2) +
      "px;margin-left:" + (0.47 * X).toFixed(2) + 'px">' + "LLM Monitor</span></div>"
    );
  }

  /* Symbol "tracé" draw-in (official loader values): segments grow from dots, pupil pops. */
  function symbolDraw(tl, svgEl, at, o) {
    const opt = o || {};
    const rect = svgEl.querySelector(".lm-sym-rect");
    const dot = svgEl.querySelector(".lm-sym-dot");
    const d = opt.duration || 0.9;
    tl.fromTo(rect, { strokeDasharray: "0.01 56.475", strokeDashoffset: -21.99, opacity: 0 },
      { strokeDasharray: "34.6 21.885", strokeDashoffset: -4.7, opacity: 1, duration: d, ease: "power3.inOut" }, at);
    tl.fromTo(dot, { scale: 0, opacity: 0, transformOrigin: "50% 50%" }, { scale: 1, opacity: 1, transformOrigin: "50% 50%", duration: d * 0.7, ease: "back.out(2.4)" }, at + d * 0.45);
  }

  /* Official quarter turn (mireSpin) on the ring only, never on a lockup. */
  function symbolQuarter(tl, svgEl, at, turns) {
    const ring = svgEl.querySelector(".lm-sym-ring");
    const n = turns || 1;
    for (let i = 0; i < n; i++) {
      tl.fromTo(ring, { rotation: i * 90, svgOrigin: "50 50" }, { rotation: (i + 1) * 90, svgOrigin: "50 50", duration: 0.62, ease: "power3.inOut", immediateRender: false }, at + i * 0.9);
    }
  }

  /* Official "balayage" scan: segments slide along the diamond, frame static. */
  function symbolScan(tl, svgEl, at, dur, loops) {
    const rect = svgEl.querySelector(".lm-sym-rect");
    const n = loops || 1;
    tl.fromTo(rect, { strokeDashoffset: -4.7 }, { strokeDashoffset: -4.7 - SYM_PERIOD * n, duration: dur, ease: "none", immediateRender: false }, at);
  }

  /* Pupil breathing (mirePulse), finite. */
  function symbolPulse(tl, svgEl, at, count, period) {
    const dot = svgEl.querySelector(".lm-sym-dot");
    const p = period || 1.3;
    for (let i = 0; i < (count || 1); i++) {
      tl.fromTo(dot, { scale: 1, opacity: 1, transformOrigin: "50% 50%" }, { scale: 0.6, opacity: 0.55, duration: p / 2, ease: "sine.inOut", immediateRender: false }, at + i * p);
      tl.fromTo(dot, { scale: 0.6, opacity: 0.55, transformOrigin: "50% 50%" }, { scale: 1, opacity: 1, duration: p / 2, ease: "sine.inOut", immediateRender: false }, at + i * p + p / 2);
    }
  }

  /* Seeded PRNG (mulberry32). */
  function rng(seed) {
    let a = seed >>> 0;
    return function () {
      a |= 0;
      a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /* Wrap each word in .lm-word spans; keeps accent spans' classes; NBSP stays inside words. */
  function splitWords(el) {
    const out = [];
    const walk = function (node, cls) {
      Array.from(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          const parts = child.textContent.split(/([ \t\n\r]+)/);
          const frag = document.createDocumentFragment();
          parts.forEach(function (p) {
            if (!p) return;
            if (/^[ \t\n\r]+$/.test(p)) {
              frag.appendChild(document.createTextNode(" "));
            } else {
              const s = document.createElement("span");
              s.className = "lm-word" + (cls ? " " + cls : "");
              s.textContent = p;
              frag.appendChild(s);
              out.push(s);
            }
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1 && !child.classList.contains("lm-word")) {
          walk(child, child.className);
          if (child.tagName === "SPAN" && child.childNodes.length) {
            while (child.firstChild) node.insertBefore(child.firstChild, child);
            node.removeChild(child);
          }
        }
      });
    };
    walk(el, "");
    return out;
  }

  /* Blur-focus word entrance. */
  function focusIn(tl, words, at, o) {
    const opt = o || {};
    tl.fromTo(
      words,
      { opacity: 0, filter: "blur(" + (opt.blur == null ? 16 : opt.blur) + "px)", y: opt.y == null ? 18 : opt.y, scale: opt.scale || 1 },
      {
        opacity: 1, filter: "blur(0px)", y: 0, scale: 1,
        duration: opt.duration || 0.7, ease: opt.ease || "power3.out",
        stagger: opt.stagger == null ? 0.07 : opt.stagger,
      },
      at
    );
  }

  /* Blur-focus exit for in-scene swaps. */
  function focusOut(tl, els, at, o) {
    const opt = o || {};
    tl.fromTo(
      els,
      { opacity: 1, filter: "blur(0px)", y: 0 },
      {
        opacity: 0, filter: "blur(" + (opt.blur || 14) + "px)", y: opt.y == null ? -10 : opt.y,
        duration: opt.duration || 0.45, ease: opt.ease || "power2.in",
        stagger: opt.stagger == null ? 0.02 : opt.stagger, immediateRender: false,
      },
      at
    );
  }

  /* Seek-safe typing. */
  function typeText(tl, el, text, at, cps) {
    const proxy = { n: 0 };
    el.textContent = "";
    const dur = text.length / (cps || 18);
    tl.fromTo(proxy, { n: 0 }, {
      n: text.length, duration: dur, ease: "none",
      onUpdate: function () { el.textContent = text.slice(0, Math.round(proxy.n)); },
    }, at);
    return dur;
  }

  /* Seek-safe counter. */
  function countUp(tl, el, from, to, at, dur, fmt, ease) {
    const proxy = { v: from };
    const f = fmt || function (v) { return String(Math.round(v)); };
    el.textContent = f(from);
    tl.fromTo(proxy, { v: from }, {
      v: to, duration: dur, ease: ease || "power2.out",
      onUpdate: function () { el.textContent = f(proxy.v); },
    }, at);
  }

  function blink(tl, el, from, to, period) {
    const p = period || 0.5;
    for (let t = from; t + p <= to + 1e-6; t += p) {
      tl.set(el, { opacity: 0 }, t + p * 0.5);
      tl.set(el, { opacity: 1 }, t + p);
    }
  }

  /* Stroke draw with a known (or measured) length. */
  function drawStroke(tl, el, at, dur, ease, len) {
    const L = len || (el.getTotalLength ? el.getTotalLength() : 1000);
    el.style.strokeDasharray = L + " " + L;
    tl.fromTo(el, { strokeDashoffset: L }, { strokeDashoffset: 0, duration: dur, ease: ease || "power2.inOut" }, at);
    return L;
  }

  /* Camera on a .world wrapper with transform-origin 0 0: put world point (px,py) at screen (sx,sy) with scale s. */
  function camState(px, py, s, sx, sy) {
    return { x: (sx == null ? 960 : sx) - px * s, y: (sy == null ? 540 : sy) - py * s, scale: s };
  }
  function cam(tl, world, from, to, at, dur, ease) {
    tl.fromTo(world, from, Object.assign({}, to, { duration: dur, ease: ease || "power3.inOut", immediateRender: false }), at);
  }

  window.LM = {
    C: C, icon: icon, logo: logo, symbol: symbol, lockup: lockup,
    symbolDraw: symbolDraw, symbolQuarter: symbolQuarter, symbolScan: symbolScan, symbolPulse: symbolPulse,
    rng: rng, splitWords: splitWords, focusIn: focusIn, focusOut: focusOut,
    typeText: typeText, countUp: countUp, blink: blink, drawStroke: drawStroke,
    camState: camState, cam: cam,
    pct: function (v) { return Math.round(v) + " %"; },
  };
})();
