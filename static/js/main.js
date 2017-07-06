(function($){
  $(function(){
    $('.button-collapse').sideNav();
  });

  function printDic(x){
      var stringOut="";
      for (var key in x)
      {
        if(key != parseInt(key, 10))
          stringOut+=key+": "+x[key]+"<br>";
      }
      return stringOut;
  };

  function printRealDic(x){
      var stringOut="";
      for (var key in x)
          stringOut+=key+": "+x[key]+"<br>";
      return stringOut;
  };

  function printRealDic2(x){
      var stringOut="";
      for (var key in x)
          if(x[key]===parseInt(x[key],10))
            stringOut+=key+": "+x[key]+"<br>";
      return stringOut;
  };

  var idarr = ['input-files','pass1','pass2','linker','simulator'];
  	for(i=0;i<idarr.length;i++)
  	{
  			$('#'+idarr[i]).hide();
  	}
  $('#submit-button').click(function(){
      files = $('input[type=file]')[0].files;
      fileNames = []
      for(i=0;i<files.length;i++){
          fileNames[i] = files[i].name;
      }

      $.ajax({
            type : "POST",
            url : "/load_ajax",
            data: JSON.stringify({files: fileNames}),
            contentType: 'application/json;charset=UTF-8',
            success: function(result) {
              response = $.parseJSON(result);
              $('#registers').html("Registers ");
              $('#memlocs').html("Variable Location");
              $('#varlocs').html("Memory Location");
              $('#currentInst').html("Nothing Loaded yet");
              $('#stack').html("Stack");
              tabs = "";
              tabs += '<div class="row" style="padding-top:10%;"><div class="col s12" tab-indicator-black><ul class="tabs tabs-fixed-width ">';
              for(i=0;i<fileNames.length;i++){
                tabs += ' <li class="tab col"><a class="brown lighten-3 brown-text text-darken-4" href="#filetab'+i+'">'+fileNames[i]+'</a></li>';
              }
              tabs += '</ul></div>';
              for(i=0;i<fileNames.length;i++){               
                tabs += '<div id="filetab'+i+'" class="col s12">';
                tabs+= '<div class="col s4 offset-s4 card-panel brown lighten-4 hoverable black-text" >'+response['filedata'][fileNames[i]].replace(/\n/g,"<br>")+'</div>';
                tabs+='</div>';
              }
              tabs += '</div>';
              $('#file-data').html(tabs);


              tabs = "";
              tabs += '<div class="row" ><div class="col s12"><ul class="tabs tabs-fixed-width">';
              for(i=0;i<fileNames.length;i++){
                tabs += ' <li class="tab col"><a class="brown lighten-3 brown-text text-darken-4" href="#pass1tab'+i+'">'+fileNames[i]+'</a></li>';
              }                    

              tabs += '</ul></div>';
              for(i=0;i<fileNames.length;i++){
                var tempname = fileNames[i].split('.')[0];
                tabs += '<div id="pass1tab'+i+'" class="col s12">';
                tabs+= '<div class="col s4 offset-s2 card-panel brown lighten-4 hoverable black-text" >'+response['pass1'][fileNames[i].split('.')[0]].replace(/\n/g,"<br>")+'</div>';
                tabs+= '<div id="tables" class="row col s4" style="display:block">';
                tabs+='<div class="col s12 card-panel brown lighten-4 hoverable black-text" > Symbols Table<br>'+printDic(response['symTable'][tempname])+'</div>';
                tabs+='<div class="col s12 card-panel brown lighten-4 hoverable black-text" > Literals Table<br>'+printRealDic(response['litTable'][tempname])+'</div>';
                tabs+='<div class="col s12 card-panel brown lighten-4 hoverable black-text" > Global Table<br>'+printDic(response['globTable'][tempname])+'</div>';
                tabs+= '</div>';
                tabs+='</div>';
              }
              tabs += '</div>';
              $('#pass1').html(tabs);
              tabs = "";
              tabs += '<div class="row"><div class="col s12"><ul class="tabs tabs-fixed-width">';
              for(i=0;i<fileNames.length;i++){
                tabs += ' <li class="tab col"><a class="brown lighten-3 brown-text text-darken-4" href="#pass2tab'+i+'">'+fileNames[i]+'</a></li>';
              }                    

              tabs += '</ul></div>';
              for(i=0;i<fileNames.length;i++){
                var tempname = fileNames[i].split('.')[0];
                tabs += '<div id="pass2tab'+i+'" class="col s12">';
                tabs+= '<div class="col s4 offset-s2 card-panel brown lighten-4 hoverable black-text " >'+response['pass2'][fileNames[i].split('.')[0]].replace(/\n/g,"<br>")+'</div>';
                tabs+= '<div id="tables" class="row col s4" style="display:block">';
                tabs+='<div class="col s12 card-panel teal  brown lighten-4 hoverable black-text" > Symbols Table<br>'+printDic(response['symTable'][tempname])+'</div>';
                tabs+='<div class="col s12 card-panel teal  brown lighten-4 hoverable black-text" > Literals Table<br>'+printRealDic(response['litTable'][tempname])+'</div>';
                tabs+='<div class="col s12 card-panel teal  brown lighten-4 hoverable black-text" > Global Table<br>'+printDic(response['globTable'][tempname])+'</div>';
                tabs+= '</div>';
                tabs+='</div>';
              }
              tabs += '</div>';
              $('#pass2').html(tabs);
              $('ul.tabs').tabs();

              $('#linkText').html('<b> Linker Output: </b><br>'+response['lin'].replace(/\n/g,"<br>"));
            }
        });
  });

  function stackString(stack){
    output = '<b>STACK: </b><br>';
    for(i=0;i<stack.length;i++)
      {
        output+= stack[i]+'<br>';
      };
    return output;
  };

  $('#loadButton').click(function(){
    offset = $('#offset').val();
    $.ajax({
          type : "POST",
          url : "/loadSimulator",
          data: JSON.stringify({file: fileNames[0].split('.')[0], 'offset':parseInt(offset)}),
          contentType: 'application/json;charset=UTF-8',
          success: function(result) {

          response = $.parseJSON(result);
          $('#registers').html('<b>REGISTERS</b><br>'+printDic(response['reg']));
          $('#memlocs').html('<b>MEMORY LOCATIONS</b><br>'+printRealDic(response['memory']));
          $('#varlocs').html('<b>VARIABLE LOCATIONS</b><br>'+printRealDic2(response['memoryData']));
          console.log(response['memoryData']);
          $('#currentInst').html('<b>CURRENT INSTRUCTION: </b>'+ response['memory'][response['reg']['PC']]);
         }   
      });
  });

  $('#runButton').click(function(){
    $.ajax({
        type : "POST",
        url : "/runSimulator",
        // data: JSON.stringify({file: fileNames[0].split('.')[0]}),
        // contentType: 'application/json;charset=UTF-8',
        success: function(result) {
          response = $.parseJSON(result);
          $('#registers').html('<b> REGISTERS</b><br>'+printDic(response['reg']));
          $('#memlocs').html('<b> MEMORY LOCATIONS</b><br>'+printRealDic(response['memory']));
          $('#varlocs').html('<b> VARIABLE LOCATIONS</b><br>'+printRealDic2(response['memoryData']));
          console.log(response['memoryData']);
          $('#currentInst').html('<b> CURRENT INSTRUCTION: </b>'+ response['memory'][response['reg']['PC']]);
          // $('#stack').html(stackString(response['stack']));

       }   
    });
  });

  $('.side-btn').click(function(){
  	var addressValue = $(this).attr("plink");
  	// alert(addressValue);
  	var idarr = ['input-files','pass1','pass2','linker','simulator','titleBox'];
  	for(i=0;i<idarr.length;i++)
  	{
  		if(idarr[i]!=addressValue)
  			$('#'+idarr[i]).hide();
  		else
  			$('#'+idarr[i]).show();
  	}
  });
})(jQuery);