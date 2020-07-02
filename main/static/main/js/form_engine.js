        function ResponseHandler(){
            this.handle = function(response){

            };

        }

        function AlertResponseHandler(){
            ResponseHandler.call(this);
            this.handle = function(response){
                if (response.result){
                   this.success(response);
                   return;
                }
                this.fail(response);

            };

            this.success = function(response){
                alert('Заявка отправлена');

            };

            this.fail = function(response){
                alert();
                let error_mesage = '';
                response.general_errors.forEach(function(error){
                    error_mesage += '/ '+error;
                });
                response.fields_errors.forEach(function(error){
                    error_mesage += '/ '+ error.id + ' ' + error.error;
                });
                alert(error_mesage);

            };

        }
        AlertResponseHandler.prototype = Object.create(ResponseHandler.prototype);

        function ajax_form_request(url, form_id, response_handler, capcha_token=null){
            let data = $('#'+form_id).serialize()+(capcha_token?('&capcha_token='+capcha_token):'');
            jQuery.post(url, data, function(response){
               //document.getElementById('id_name').setCustomValidity('sdfsdfsf</br>sfsdfdsfs');
               if (response.result){
                   document.getElementById(form_id).reset()
                   response_handler.handle(response);
                   return
               }
               response_handler.handle(response);


            }, "json");

        }


        function onClick() {
            grecaptcha.ready(function() {
                grecaptcha.execute('6LeeTqoZAAAAAByyQfzBY7MzV8hIrZFcq_jobOdR', {action: 'submit'}).then(function(token) {

                });
            });
        }

        function addFormSubmitListner(url, form_id, response_handler){
            document.getElementById(form_id).addEventListener('submit', function(e){
                e.preventDefault();
	            ajax_form_request(url, form_id, response_handler);

             });

        }