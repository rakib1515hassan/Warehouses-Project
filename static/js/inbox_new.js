let input_message = $('#input-message')
let message_body = $('.msg_card_body')
let send_message_form = $('#send-message-form')
const USER_ID = $('#logged-in-user').val()
const USER_NAME = $('#selfname').val()
    send_message_form.on('submit', function (e){
        e.preventDefault()
        let message = input_message.val()
        let send_to = get_active_other_user_id()
        let thread_id = get_active_thread_id()
        let image=""+$('#selfimg').attr('src')
        $('#input-message').val("");
        let data = {
            'message': message,
            'sent_by': USER_ID,
            'send_to': send_to,
            'thread_id': thread_id,
            'image':image,
        }
        console.log(data)
        $.ajax({
      url: 'chat/send_message/',
      type: 'post',
      data: data,
      success: function(response) {
        //success call
          var nowtime = new Date().toLocaleTimeString()
          newMessage(message,USER_NAME,nowtime,image, USER_ID, thread_id,response.message_id)
      },
      error: function (error){

           alert("Somthing wrong happend!!");
                return;
      }
    });
        $(this)[0].reset()
    })

setInterval(() => {
  fetch('chat/get_messages/')
    .then(response => response.json())
    .then(data => {
      // do something with the data
      data.threads.forEach(thread => {

          thread.messages.forEach(message=>{
              let existing_message = $(`.chat-message[chat-id="${thread.id}"] .chat [data-message-id="${message.id}"]`);
                  if (existing_message.length > 0) {
                    // Message already in HTML, don't add it again

                    return false;
                  }
                  else {
                      var time = new Date(message.created_at).toLocaleTimeString();
                      newMessage(message.message, message.user, time, message.user, message.user_id, thread.id, message.id);
                  }
          });



      });
    })
    .catch(error => {
      console.error(error);
    });
}, 5000);


function newMessage(message, name, time, uimg, sent_by_id, thread_id, message_id) {

  if ($.trim(message) === '') {
    return false;
  }
  let message_element;
  let chat_id = 'chat_' + thread_id;
  if (sent_by_id == USER_ID) {
    message_element = `
    <div class="d-flex justify-content-end mb-10" data-message-id="${message_id}">
										<!--begin::Wrapper-->
										<div class="d-flex flex-column align-items-end">
											<!--begin::User-->
											<div class="d-flex align-items-center mb-2">
												<!--begin::Details-->
												<div class="me-3">
													<span class="text-muted fs-7 mb-1">${time}</span>
													<a href="#"
														class="fs-5 fw-bold text-gray-900 text-hover-primary ms-1">You</a>
												</div>
												<!--end::Details-->
												<!--begin::Avatar-->
												<div class="symbol symbol-35px symbol-circle">
													<img alt="Pic" src="https://bootdey.com/img/Content/user_1.jpg" id="selfimg" />
												</div>
												<!--end::Avatar-->
											</div>
											<!--end::User-->
											<!--begin::Text-->
											<div class="p-5 rounded bg-light-primary text-dark fw-semibold mw-lg-400px text-end"
												data-kt-element="message-text">${message}</div>
											<!--end::Text-->
										</div>
										<!--end::Wrapper-->
									</div>
    `;
  } else {
    message_element = `
      	<div class="d-flex justify-content-start mb-10" data-message-id="${message_id}">
										<!--begin::Wrapper-->
										<div class="d-flex flex-column align-items-start">
											<!--begin::User-->
											<div class="d-flex align-items-center mb-2">
												<!--begin::Avatar-->
												<div class="symbol symbol-35px symbol-circle">
													<img alt="Pic" src="assets/media/avatars/300-25.jpg" />
												</div>
												<!--end::Avatar-->
												<!--begin::Details-->
												<div class="ms-3">
													<a href="#"
														class="fs-5 fw-bold text-gray-900 text-hover-primary me-1">${name}</a>
													<span class="text-muted fs-7 mb-1">${time}</span>
												</div>
												<!--end::Details-->
											</div>
											<!--end::User-->
											<!--begin::Text-->
											<div class="p-5 rounded bg-light-info text-dark fw-semibold mw-lg-400px text-start"
												data-kt-element="message-text">${message}</div>
											<!--end::Text-->
										</div>
										<!--end::Wrapper-->
									</div>
    `;
  }

  let message_body = $('.chat-message[chat-id="' + chat_id + '"] .chat .message');
  // Check if message is already in HTML
  let existing_message = $(`.chat-message[chat-id="${chat_id}"] .chat .message [data-message-id="${message_id}"]`);
  if (existing_message.length > 0) {
    // Message already in HTML, don't add it again

    return false;
  }
  message_body.append($(message_element));
  $('.chat-message[chat-id="' + chat_id + '"] .chat .message').animate({
    scrollTop: $('.chat-message[chat-id="' + chat_id + '"] .chat .message').prop("scrollHeight")
  }, 500);
  input_message.val(null);
}

let rimage=""


$('.no-thread').on('click', function (){
     let cuser_id = $(this).attr('cuser-id')
        cuser_id=cuser_id.replace('cuser_', '')
     rimage=""+$('#nimg'+cuser_id).attr('src')
    let your_image=""+$('#selfimg').attr('src')
    let data = {
             'target_user':cuser_id,
                'request_image':your_image,
        }
        data = JSON.stringify(data)
        socket.send(data)
    console.log("no thread")

    $('#mycard' ).remove('.no-thread[cuser-id="' + cuser_id + '"]');

})

function get_active_other_user_id(){
    let other_user_id = $('.chat-message.is_active').attr('other-user-id')
    other_user_id = $.trim(other_user_id)
    return other_user_id
}

function get_active_thread_id(){
    let chat_id = $('.chat-message.is_active').attr('chat-id')
    let thread_id = chat_id.replace('chat_', '')
    return thread_id
}