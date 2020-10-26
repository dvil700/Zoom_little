//Class
function AbstractResponseHandler(){
    this.handle = function(response){

    };

}


//Class
function AbstractFormResultView(){
    this.render = function(response){

    }
}


//Class
function ResponseHandler(success_view, fail_view){
    AbstractResponseHandler.call(this);

    this.success_view = success_view;
    this.fail_view = fail_view;

    this.handle = function(response){
        if (response.result){
            this.success_view.render(response);
            return;
        }
        this.fail_view.render(response);

    }; 

}
ResponseHandler.prototype = Object.create(AbstractResponseHandler.prototype);


//Class
function AlertSuccessFormResultView(success_msg, form_mediator){
    AbstractFormResultView.call(this);
    this.success_msg = success_msg;
    this.form_mediator = form_mediator;


    this.render = function(response){
        this.form_mediator.resetForms();
        alert(this.success_msg);
    };

}
AlertSuccessFormResultView.prototype = Object.create(AbstractFormResultView.prototype);


//Class
function AlertFailFormResultView(){
    AbstractFormResultView.call(this);

    this.render = function(response){
            alert();
            let error_message = '';
            response.general_errors.forEach(function(error){
                error_message += '/ '+error;
             });
     
            response.fields_errors.forEach(function(error){
                error_message += '/ '+ error.id + ' ' + error.error;
            });
            alert(error_message);
    };

}
AlertFailFormResultView.prototype = Object.create(AbstractFormResultView.prototype);


//Class
function FailFormResultView(form_mediator){
    AbstractFormResultView.call(this);
    this.form_mediator = form_mediator; 

    this.generalErrorsRender = function(response){
        let error_message = '';
        response.general_errors.forEach(function(error){
            error_message += '/ '+error;
         });
        if (error_message){
            alert(error_message);
        } 

    };


    this.render = function(response){
        this.generalErrorsRender(response);
        
        response.fields_errors.forEach(function(error){
            this.form_mediator.addFieldError(error.id, error.error);
        }, this);

    };

}
FailFormResultView.prototype = Object.create(AbstractFormResultView.prototype);


function OnInputEventManager(){
    this.manager = null;
    this.event_listner_function = null;

    this.attach = function(error_manager){
        this.manager = error_manager;
    };

    this.getEventListnerFunction = function(){
        if (this.event_listner_function ) return this.event_listner_function;
        let error_manager = this.manager;
        let fn = function(e){
            error_manager.removeError(this.id);
            this.removeEventListener('input', fn); 
        };
        this.event_listner_function = fn;
        return fn;

    };

    this.setEvent = function(){
        if (!this.manager) return;
        this.manager.getField().addEventListener('input', this.getEventListnerFunction());
    }

}


function ErrorEntityFactory(hint_element_html_class_name=null){
    hint_element_html_class_name = hint_element_html_class_name?hint_element_html_class_name:'js_errorMessage_default_cls';
    this.hint_element_class = 'class="'+hint_element_html_class_name+'"';
    
    this.getCss = function(element){
        return {'left': jQuery(element).offset().left,
        'top': jQuery(element).offset().top - 20,
       // 'background-color':'#e74c3c',
       // 'border': '1px solid black',
        'border-radius': '5px',
        'color': '#e74c3c', //'#fff',
        'font-family': 'Arial',
        'font-size': '12px',
        'margin': '3px 0 0 0px',
        'padding': '6px 5px 5px',
        'position': 'absolute',
        'z-index': '9999'};
    };


    this.create = function(elem) {
        $(".js_errorMessage").remove();
        error_message_elem = jQuery('<div '+this.hint_element_class+'>' + '</div>');
        error_message_elem.appendTo('body').css(this.getCss(elem));
        jQuery(elem).focus();
        return error_message_elem[0];
    };
   
}



function ErrorManager(error_entity_factory, event_managers=null){
    
    this.error_entity_factory = error_entity_factory; // factory that creates the error message DOM element 
    this.form_element = null;
    this.current_error_msg = null;
    this.event_managers = new Array();
        

    this.addEventManager = function(event_manager){
        event_manager.attach(this);
        this.event_managers.push(event_manager); 
    };


    if (event_managers){
        event_managers.forEach(function(event_manager){
           this.addEventManager(event_manager);   
        }, this);

    }


    this.setField = function(form_element){
        this.form_element = form_element;
    };

    this.getField = function(){
        return this.form_element;
    };
    
    this.replaceTags=function(str){
        return str.replace(/<\/?[^>]+>/g,'');
        
    };

    this.handleError = function(error_msg){
        if (!this.current_error_msg) this.current_error_msg = this.error_entity_factory.create(this.form_element);
        this.current_error_msg.append(this.replaceTags(error_msg));
        this.event_managers.forEach(function(event_manager){
           event_manager.setEvent();
        }, this);
    };

    this.removeError = function(){
        if (!this.current_error_msg) return;
        this.current_error_msg.remove();
        this.current_error_msg = null;
    };

}


function FormMediator(){
    this.fields = {};
    this.forms = new Set();
    this.addField = function(field_id, err_manager){
       let elem = document.getElementById(field_id);
       this.fields[field_id] = {elem: elem, error_manager: err_manager};
       err_manager.setField(elem);
       this.forms.add(elem.form);

    };

    this.addFieldError = function(elem_id, msg){
       this.fields[elem_id].error_manager.handleError(msg);
    };
 
    this.removeErrorMsg = function(elem_id){
       this.fields[elem_id].error_manager.removeError();
    };

    this.removeAllErrors = function(){
       this.fields.forEach(function(field){
           field.error_manager.removeError();
       });
   }
   
   this.resetForms = function(){
       this.forms.forEach(function(form){
           form.reset();
       }, this);
   }

}


function FormMediatorFactory(){
    this.getInputFieldErrorManager = function(){
        return new ErrorManager(new ErrorEntityFactory, [new OnInputEventManager()]);
    };

    this.getMediator = function(form){
        let mediator = new FormMediator();

        for (let i=0; i<form.elements.length;i++){
            let elem =form.elements[i];
            if (elem.tagName == 'INPUT'&&elem.id) mediator.addField(elem.id, this.getInputFieldErrorManager());
        }
        return mediator;
    }


}


function ResponseHandlerFactory(form_mediator, success_msg = 'Данные успешно отправлены'){
    this.form_mediator = form_mediator;
    this.success_msg = success_msg; 
    this.getResponseHandler= function(){
        success_view = new AlertSuccessFormResultView(this.success_msg, form_mediator);
        fail_view = new FailFormResultView(this.form_mediator);
        return new ResponseHandler(success_view, fail_view);
    }

}


function ajax_form_request(url, form_id, response_handler, capcha_token=null){
    let data = $('#'+form_id).serialize()+(capcha_token?('&captcha_token='+encodeURI(capcha_token)):'');
    jQuery.post(url, data, function(response){
       if (response.result){
           document.getElementById(form_id).reset()
           response_handler.handle(response);
           return;
       }
       response_handler.handle(response);


    }, "json");
}



function addFormSubmitListner(url, form_id, response_handler, captcha_site_key){
    document.getElementById(form_id).addEventListener('submit', function(e){
        e.preventDefault();
        grecaptcha.ready(function() {
            grecaptcha.execute(captcha_site_key, {action: 'submit'}).then(function(token) {
	            ajax_form_request(url, form_id, response_handler, token);
             });
        });
     });

}







