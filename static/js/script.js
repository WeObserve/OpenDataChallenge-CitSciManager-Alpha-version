function upload_files_to_s3() {
                const id = $(this).attr('id');
                console.log(id);
                if (validate_files(this.files, id)){
                     $.each(this.files , (i , v) => {
                         get_signed_request(v, i);
                     });
                    $(".enable-on-validate").prop("disabled",false);
                }
                else {
                    $(".enable-on-validate").prop("disabled",true);

                }
}


function validate_files(files, id){
    let result = true;
    if (files.length > 0) {
        let total_size = 0;
        if (id === "raw_data_files"){
            const raw_file_extension = ['jpeg', 'jpg', 'png'];
             $.each(files , (i , v) => {
                 console.log(v.name);
                  let file_size = v.size;
                  let file_name = v.name;
                  total_size = total_size + file_size;
                  if ($.inArray(file_name.split('.').pop().toLowerCase(), raw_file_extension) === -1) {
                        result = false;
                        alert("Only formats are allowed : "+raw_file_extension.join(', '));
                }
                  else{
                      $('.filenames').append('<div class="name">' + file_name +'  '+ file_size +' bytes</div>');
                  }
             });
             $('.filesize').text('Total size of files: ' +(total_size/1024) +'KB');
             if (total_size/(1024*1024*1024) > 2) {
                result = false;
                alert("Total file size is greater than 2GB")
            }
        }
        else if (id === "metadata_files") {
            const meta_file_extension = ['csv'];
           $.each(files , (i , v) => {
               let file_size = v.size;
               let file_name = v.name;
               total_size = total_size + file_size;
               if ($.inArray(file_name.split('.').pop().toLowerCase(), meta_file_extension) === -1) {
                    result = false;
                    alert("Only CSV formats are allowed");
                }
               else {
                   $('.filenames').append('<div class="name">' + file_name +'  '+ file_size +' bytes</div>');
               }
             });
            $('.filesize').text('Total size of files: ' +(total_size/1024) +'KB');
            if (total_size/(1024*1024*1024) > 2) {
                result = false;
                alert("Total file size is greater than 2GB")
            }
        }

    }
    else {
        alert("No files selected")
    }

    return result;
}


function get_signed_request(file, i) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET","/sign_s3?file_name="+file.name+"&file_type="+file.type);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if(xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                console.log(response.data.fields.key);
                console.log(response.url);
                upload_file(file, response.data, response.url, i);
            }
            else {
                error.textContent = "Could not get a signed URL";
                error.style.color = 'red';
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
                error.textContent = "Could not upload file";
                error.style.color="red";
            }
        }
    };
    xhr.send(post_data);
}



$(document).ready(function() {
        $('#summernote').summernote({
          placeholder: 'Add story here..'
        });
        $('[data-toggle="tooltip"]').tooltip({
            placement : 'top'
        });
        $('#raw_data_files').change(upload_files_to_s3);
        $('#metadata_files').change(upload_files_to_s3);
      });