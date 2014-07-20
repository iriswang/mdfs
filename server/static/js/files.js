$(document).ready(function() {
	mdfs.setCurrentDirectory("/");
	mdfs.getRootDirectory();


	var obj = $("#draganddrop");
	console.log(obj);
	obj.on('dragenter', function (e) 
	{
	    e.stopPropagation();
	    e.preventDefault();
	    $(this).css('border', '2px solid #0B85A1');
	});
	obj.on('dragover', function (e) 
	{
	     e.stopPropagation();
	     e.preventDefault();
	});
	obj.on('drop', function (e) 
	{
	 
	     $(this).css('border', '2px dotted #0B85A1');
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
	  obj.css('border', '2px dotted #0B85A1');
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