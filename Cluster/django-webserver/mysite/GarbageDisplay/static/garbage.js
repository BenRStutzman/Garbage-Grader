var need_weight = false;
const PICS_ON_SCREEN = 2;

$(document).ready(function() {
  update()
})

function update(){
  var first = $('#pictures').children().first()[0].id;
  // console.log(first);

  $.ajax({
    'type':'GET',
    'data':{'id': first, 'need_weight': need_weight},
    'url': 'update/',
    'success': function (data) {

      // console.log(data);

      var num_to_remove = data.match(/<div/g);
      if(num_to_remove != null){
        if(num_to_remove.length != 0){

          for(var i = 0;i < num_to_remove.length; i++){
            $('#pictures').children().last().remove();
            console.log(num_to_remove);
          }

          $('#pictures').prepend(data);

          var flash_color;

	        switch ( $('.grade')[0].textContent.trim() ) {
	          case 'A':
	            flash_color = '#03fc0f'; // Green
	            break;
	          case 'B':
	            flash_color = '#fcd703'; // Yellow
	            break;
	          case 'C':
	            flash_color = '#fc7303'; // Orange
	            break;
	          case 'D':
	            flash_color = '#fc0303'; // Red
	            break;
	          case 'F':
              flash_color = '#cc00ff'; // Purple
              break;
	          default:
	            flash_color = '#00bef7';
	        }


          first = $('#pictures').children().first()[0].id;

          // New picture grows in from right
          $('#' + first).css('width', '0px');
          $('#' + first).animate( {width: '950'}, 500);

          // Flashes a color depending on grade, then fades to blue
	        $('#' + first).css('background-color', flash_color);
	        setTimeout(function () {
	          $('#' + first).animate( {backgroundColor: '#00bef7'}, 500);
	        }, 1000);

          for(i = 0; i<$('.weight').length; i++){
            // debugger;
            var weight = Number($('.weight')[i].textContent);
            if (weight == 0) {need_weight = true; break;}
          }
        }
      }

      update();
    }
  });

}
