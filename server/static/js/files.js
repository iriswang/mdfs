$(document).ready(function() {
	mdfs.setCurrentDirectory("/");
	mdfs.getRootDirectory();

	$(".profile-picture").css("background", "url('" + window.url + "') no-repeat center center;");


	var obj = $("#draganddrop");
	console.log(obj);
	obj.on('dragenter', function (e) 
	{
	    e.stopPropagation();
	    e.preventDefault();
	    $(this).css('box-shadow', 'inset 0 0 0 1px rgba(255,255,255,0.1), 0 1px 1px rgba(0,0,0,0.1)');
	    $(".ch-info").css('transform', 'scale(1)');
	    $(".ch-info").css('opacity', 1);
	    $(".ch-info p").css('opacity', 1);
	});
	obj.on('dragover', function (e) 
	{
	     e.stopPropagation();
	     e.preventDefault();
	});
	obj.on('drop', function (e) 
	{
	 
	     e.preventDefault();
	     var files = e.originalEvent.dataTransfer.files;
	 
	     //We need to send dropped files to Server
	     handleFileUpload(files,obj);
	});


	$(document).on('dragenter', function (e) 
	{
	    e.stopPropagation();
	    e.preventDefault();
	});
	$(document).on('dragover', function (e) 
	{
	  e.stopPropagation();
	  e.preventDefault();
	});
	$(document).on('drop', function (e) 
	{
	    e.stopPropagation();
	    e.preventDefault();
	});


	function handleFileUpload(files, obj)
	{
	   for (var i = 0; i < files.length; i++) 
	   {
	        var fd = new FormData();
	        fd.append('file', files[i]);
	        // fd.append('path_to_file', mdfs.getCurrentDirectory());
	 
	        // var status = new createStatusbar(obj); //Using this we can set progress.
	        // status.setFileNameSize(files[i].name,files[i].size);
	        sendFileToServer(fd);
	 
	   }
	}

	function sendFileToServer(formData)
	{

		console.log('-->', formData);
	    var uploadURL ="/upload?path=" + mdfs.getCurrentDirectory(); //Upload URL
	    var extraData ={}; //Extra Data.
	    var jqXHR=$.ajax({
	        url: uploadURL,
	        type: "POST",
	        contentType:false,
	        processData: false,
	        cache: false,
	        data: formData,
	        scriptCharset: "utf-8",
	        success: function(data){
	        	console.log(data);
	            console.log("file upload complete!");
	            //$("#status1").append("File upload Done<br>");           
	        }
	    }); 
	    // status.setAbort(jqXHR);
	}
});