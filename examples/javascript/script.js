function param(object) {
    var encodedString = '';
    for (var prop in object) {
        if (object.hasOwnProperty(prop)) {
            if (encodedString.length > 0) {
                encodedString += '&';
            }
            encodedString += encodeURI(prop + '=' + object[prop]);
        }
    }
    return encodedString;
}

function signed() {
    var r = new XMLHttpRequest();
    r.open("GET", "http://localhost:1234/signed/example", true);
    r.send();
}

function read() {
    var r = new XMLHttpRequest();
    r.open("POST", "http://localhost:1234/read", true);
    r.setRequestHeader('Content-Type', 'application/json');
    r.onreadystatechange = function () {
      if (r.readyState != 4 || r.status != 200) return;
      console.log("Success: " + JSON.parse(r.responseText));
    };
    r.send(JSON.stringify({
        'text': document.getElementById('text').value,
        'level': 100,
        'volume': 100,
        'speed': 100 
    }));
}
