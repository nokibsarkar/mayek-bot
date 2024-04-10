let f = new FormData();
f.append("text", "अभिनव");
await fetch("http://localhost:5000/api/transliterate", {
    "credentials": "include",
    "method": "POST",
    "mode": "cors",
    "body": f
}).then(response => response.text())