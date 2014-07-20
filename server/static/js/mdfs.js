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
        data: {path: _stripTrailingSlash(path)},
        success: function(json)  {
            console.log(json);
            console.log('cd into: ' + path);
            // first thing to do, change the directory
            mdfs.setCurrentDirectory(path);

            mdfs.ls(path, json.data.files);
            mdfs.setNavToCurrentDirectory(path);
        },
        dataType: "json"
    });
}

/* call this everytime we show a new directory */
mdfs.ls = function(path, filenames){
    console.log(filenames);
    $(".directory-container").html(_lsHTML(filenames));
    $(".table-row").click(function() {

        // for each row add current directory to newPath
        var newPath = $(this).data("cd");
        console.log(newPath);
        mdfs.cd(newPath);
    });
}

/* string representing path */
mdfs.setCurrentDirectory = function(path) {
    console.log('current directory set to: ' + path);
    return localStorage.setItem("mdfspath", path);
}

mdfs.getCurrentDirectory = function() {
     return localStorage.getItem("mdfspath");
}

/* dive down into the directory named dirname */
mdfs.dive = function(dirname) {
    console.log("DIVE INTO" + dirname);
}

/* assumes no / in dir names <-- lol wat */
mdfs.setNavToCurrentDirectory = function(path) {
    var layers = path.split('/');
    console.log("path: " + path + " split into layers: " + layers)
    var html = "<div class='navigation-bar-container'>";

    /* build up link */
    var soFarLink = "/";
    /* deal with root '/' */
    html += _navHTML(soFarLink, "/");
    $(layers).each(function(index, layer) {
        if (layer) {
            /* theres usually a trailing / but it got split off... */
            layer = layer + "/";
            soFarLink = soFarLink + layer;
            html += _navHTML(soFarLink, layer);
        }
    });
    console.log(html);
    $(".navigation-container").html(html + "</div>");
    $(".nav-layer").click(function() {
        var newPath = $(this).data("cd");
        mdfs.cd(newPath);
    });
}

mdfs.downloadFile = function(path, filename) {
    // downloadstheFile 
}

/* individual nav layers layer: layer name ... link: path to layer */
_navHTML = function(link, layer) {
    var html = "<a class='nav-layer' href='#' data-cd='" + link + "'>" + layer + "</a>";
    return html;
}

_lsHTML = function(filenames) {
    var header = "" + 
    "<table class='directory table'>" + 
      "<thead>" + 
          "<tr><th>Name</th><th>Kind</th></tr>" + 
      "</thead>";
    
    var body = "<tbody>";
    $(filenames).each(function(index, f) {
        body += "<tr class='table-row' data-cd='" + _appendCurrentDirectoryToPath(f) + "'><td class='filename-td'>" + _filenameToIconNameFormat(f) + "</td><td>" + _filenameToKind(f) + "</td></tr>";
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

/* assumes current directory has trailing / and directory doesn't have beginning / but does have trailing / */
_appendCurrentDirectoryToPath = function(directory) {
    console.log('appending: ' + mdfs.getCurrentDirectory());
    return mdfs.getCurrentDirectory() + directory;
}

_createIcon = function(iconName) {
    return "<i class='file-icon pe-7s-" + iconName + "'></i>"
}

_stripTrailingSlash = function(string) {
    if (string.slice(-1) == "/") {
        return string.slice(0, - 1);
    }
    return string;
}
})(jQuery);