let input_message = $('#input-message')
let message_body = $('.msg_card_body')
let send_message_form = $('#send-message-form')
const USER_ID = $('#logged-in-user').val()
const USER_NAME = $('#selfname').val()
    console.log('open')
    send_message_form.on('submit', function (e){
           console.log("message")
   console.log($(".messageText").text())
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
      url: 'send_message/',
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
  fetch('get_messages/')
    .then(response => response.json())
    .then(data => {
      // do something with the data
      data.threads.forEach(thread => {

          thread.messages.forEach(message=>{
              let existing_message = $(`.messages-wrapper[chat-id="${thread.id}"] .chat-container .msg_card_body [data-message-id="${message.id}"]`);
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
      <li class="chat-right" data-message-id="${message_id}">
        <div class="chat-hour">${time} <span class="fa fa-check-circle"></span></div>
        <div class="chat-text">${message}</div>
        <div class="chat-avatar">
          <img src="${uimg}" alt="Not Found" onerror=this.src="https://t4.ftcdn.net/jpg/00/84/67/19/360_F_84671939_jxymoYZO8Oeacc3JRBDE8bSXBWj0ZfA9.jpg">
          <div class="chat-name">${name}</div>
        </div>
      </li>
    `;
  } else {
    message_element = `
      <li class="chat-left" data-message-id="${message_id}">
        <div class="chat-avatar">
          <img src="${uimg}" alt="Not Found" onerror=this.src="https://t4.ftcdn.net/jpg/00/84/67/19/360_F_84671939_jxymoYZO8Oeacc3JRBDE8bSXBWj0ZfA9.jpg">
          <div class="chat-name">${name}</div>
        </div>
        <div class="chat-text">${message}</div>
        <div class="chat-hour">${time} <span class="fa fa-check-circle"></span></div>
      </li>
    `;
  }

  let message_body = $('.messages-wrapper[chat-id="' + chat_id + '"] .chat-container .msg_card_body');
  // Check if message is already in HTML
  let existing_message = $(`.messages-wrapper[chat-id="${chat_id}"] .chat-container .msg_card_body [data-message-id="${message_id}"]`);
  if (existing_message.length > 0) {
    // Message already in HTML, don't add it again

    return false;
  }
  message_body.append($(message_element));
  $('.messages-wrapper[chat-id="' + chat_id + '"] .chat-container').animate({
    scrollTop: $('.messages-wrapper[chat-id="' + chat_id + '"] .chat-container').prop("scrollHeight")
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
    let other_user_id = $('.messages-wrapper.is_active').attr('other-user-id')
    other_user_id = $.trim(other_user_id)
    return other_user_id
}

function get_active_thread_id(){
    let chat_id = $('.messages-wrapper.is_active').attr('chat-id')
    let thread_id = chat_id.replace('chat_', '')
    return thread_id
}