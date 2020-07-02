        function ajax_form_request(url, form_selector, capcha_token=null){
            data = form_selector.serialize()+(capcha_token?('&capcha_token='+capcha_token):'');
            $.ajax({
                url: url,
                method: "POST",
                data: data,
                    success: function(response){
                       $('#callback_form').html(response);
                       addButtonOnclickListner(url, form_selector, capcha_token);

                    },
                    fail: function(response){
                       alert('Произошла ошибка в процессе отправки. Попробуйте снова позже');
                    }
            });

        }


        function onClick() {
            grecaptcha.ready(function() {
                grecaptcha.execute('6LeeTqoZAAAAAByyQfzBY7MzV8hIrZFcq_jobOdR', {action: 'submit'}).then(function(token) {

                });
            });
        }

        function addButtonOnclickListner(url, form_selector){
            document.getElementById('submit_button').addEventListener('click', function(e){
                e.preventDefault();
	            ajax_form_request(url, form_selector);

             });

        }