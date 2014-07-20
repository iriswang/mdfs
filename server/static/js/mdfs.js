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
        success: callback(data),
        dataType: "json"
    });
}

mdfs.accessTokenCallback = function(json){
    console.log(json);
}

})(jQuery);
