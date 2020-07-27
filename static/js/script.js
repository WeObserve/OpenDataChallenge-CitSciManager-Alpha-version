function upload_files_to_s3() {
                var totalsize = 0;
                 $.each(this.files , (i , v) => {
                    var filename = v.name;
                    var filesize = v.size;
                    totalsize = totalsize + filesize;
            $('.filenames').append('<div class="name">' + filename +'  '+ filesize +' bytes</div>');
            get_signed_request(v, i);

    });
                 $('.filesize').text('Total size of files: ' +(totalsize/1024) +'KB');

            }

function get_signed_request(file, i) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET","/sign_s3?file_name="+file.name+"&file_type="+file.type);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if(xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                console.log(response.data.fields.key)
                console.log(response.url)
                upload_file(file, response.data, response.url, i);
            }
            else {
                alert("Could not get a signed URL");
            }
        }
    };
    xhr.send();
}

function upload_file(file, s3_data, url,i){
    var xhr = new XMLHttpRequest();
    xhr.open("POST", s3_data.url);
    console.log(s3_data.url);
    var post_data = new FormData();
    for (key in s3_data.fields) {
        post_data.append(key, s3_data.fields[key]);
    }
    post_data.append('file',file);

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4){
            if (xhr.status === 200 || xhr.status === 204){
             $('.urls').append('<input type="hidden" id="url"'+i+' name="s3url-hidden" value="'+ url +'">');
             $('.relative-paths').append('<input type="hidden" id="rpath"'+i+' name="s3rpath-hidden" value="'+ s3_data.fields.key +'">');
            }
            else {
                alert("Could not upload file");
            }
        }
    };
    xhr.send(post_data);
}



$(document).ready(function() {
        $('#summernote').summernote({
          placeholder: 'Add story here..'
        });
        $('#raw_data_files').change(upload_files_to_s3)
        $('#metadata_files').change(upload_files_to_s3)
      });