var mdfs = mdfs || {};

(function ($) {

_formatAccessToken = function(service, accessToken) {
    return {'access_token': accessToken, 'service': service};
}

mdfs.postAccessToken = function(service, accessToken, callback) {
    data = _formatAccessToken(service, accessToken);
    $.ajax({
        type: "POST",
        url: "/initialize",
        data: data,
        success: function(json) {
            mdfs.accessTokenCallback(json);
        },
        dataType: "json"
    });
}

mdfs.accessTokenCallback = function(json){
    console.log(json);
}

mdfs.getRootDirectory = function(){
    console.log("getRootDirectory()");
    mdfs.cd("/");
}

/* more general case of getRootDirectory, renders files at path */
mdfs.cd = function(path) {
    $.ajax({
        type: "GET",
        url: "/readdir",
        data: {path: path},
        success: function(json)  {
            mdfs.ls(path, json.data.files);
            mdfs.setCurrentDirectory(path);
            mdfs.setNavToCurrentDirectory(path);
        },
        dataType: "json"
    });
}

/* call this everytime we show a new directory */
mdfs.ls = function(path, filenames){
    console.log(filenames);
    $(".directory-container").html(_lsHTML(filenames));
}

/* string representing path */
mdfs.setCurrentDirectory = function(path) {
    localStorage.setItem("mdfs_path", path);
}

mdfs.getCurrentDirectory = function() {
     localStorage.getItem("mdfs_path");
}

/* dive down into the directory named dirname */
mdfs.dive = function(dirname) {
    console.log("DIVE INTO" + dirname);
}

/* assumes no / in dir names <-- lol wat */
mdfs.setNavToCurrentDirectory = function(path) {
    var layers = path.split('/');
    $(layers).each(function(index, layer) {
        /* need to send path up to that layer */
        // _
    });
}

mdfs.downloadFile = function(path, filename) {
    // downloadstheFile 
}

/* individual nav layers layer: string */
_navHTML = function(layer) {

}

_lsHTML = function(filenames) {
    var header = "" + 
    "<table class='directory table'>" + 
      "<thead>" + 
          "<tr><th>Name</th><th>Kind</th></tr>" + 
      "</thead>";
    
    var body = "<tbody>";
    $(filenames).each(function(index, f) {
        body += "<tr class='table-row' data-filename='" + f + "'><td class='filename-td'>" + _filenameToIconNameFormat(f) + "</td><td>" + _filenameToKind(f) + "</td></tr>";
    });
    body += "</tbody>"
    return header + body + "</table>";
}

// is it a filename or dir name
_filenameToKind = function(filename) {
    if (filename.slice(-1) == "/") {
        return "folder"
    } else {
        return "document"
    }
}

// returns html for an icon and filename
_filenameToIconNameFormat = function(filename) {
    if (_filenameToKind(filename) == "folder") {
        return _createIcon("folder") + filename
    } else {
        return _createIcon("paper-plane") + filename
    }
}

_appendCurrentDirectoryToPath = function(directory) {
    console.log('not implemented');
}

_createIcon = function(iconName) {
    return "<i class='file-icon pe-7s-" + iconName + "'></i>"
}

})(jQuery);
