// function total(){
// 	var quantity1 = Math.round(parseFloat(document.getElementById('volleyball_quantity').value));
// 	var price1 = parseFloat(document.getElementById('volleyball_price').value);
// 	var quantity2 = Math.round(parseFloat(document.getElementById('basketball_quantity').value));
// 	var price2 = parseFloat(document.getElementById('basketball_price').value);
// 	var subtotal1 = quantity1*price1;
// 	var subtotal2 = quantity2*price2;
// 	document.getElementById('volleyball_subtotal').value = subtotal1;
// 	document.getElementById('basketball_subtotal').value = subtotal2;
// 	var grandtotal=subtotal1+subtotal2;
// 	if (document.getElementById('shipping').checked){
// 		grandtotal = grandtotal + parseFloat(document.getElementById('shipcost').value);
// 	}
// 	document.getElementById('grandtotal').value=grandtotal;
// 	// console.log(document.form1.length);
//
// }


function validate(){

    alert("Hello")


    // var form1 = document.form1;
    // var text = "<hr><h2>Thanks for shopping with us!<p> Here is your receipt: </p></h2><p style='text-align:center; border: 2px dotted white'>";
    // var valid = true;
    //
    // //Validating if qunatities entered are not both zero and if both are integers.
    // var quantity1 = document.getElementById('volleyball_quantity').value;
    // var quantity2 = document.getElementById('basketball_quantity').value;
    //
    // if ((quantity1=='0') && (quantity2=='0')){
    // 	alert ("Please enter a valid quantity (>0) for at least one of the fields indicated.");
    // 	document.getElementById('volleyball_quantity').focus();
    // 	document.getElementById('volleyball_quantity').select();
    // 	document.getElementById('volleyball_quantity').style.backgroundColor="red";
    // 	document.getElementById('basketball_quantity').focus();
    // 	document.getElementById('basketball_quantity').select();
    // 	document.getElementById('basketball_quantity').style.backgroundColor="red";
    // 	valid=false;
    //
    // } else if (Number.isInteger(parseFloat(quantity1))==false){
    // 	alert("Please enter an integer quantity for the indicated field.");
    // 	document.getElementById('volleyball_quantity').focus();
    // 	document.getElementById('volleyball_quantity').select();
    // 	document.getElementById('volleyball_quantity').style.backgroundColor="red";
    // 	valid=false;
    // } else if (Number.isInteger(parseFloat(quantity2))==false){
    // 	alert("Please enter an integer quantity for the indicated field.");
    // 	document.getElementById('basketball_quantity').focus();
    // 	document.getElementById('basketball_quantity').select();
    // 	document.getElementById('basketball_quantity').style.backgroundColor="red";
    // 	valid=false;
    // }
    //
    // //Validating checkbox for delivery type.
	// if (valid==true){
	// var obj = document.form1.delivery;
    // var len = obj.length;
    // var chosen = null;
    // for (var j = 0; j <len; j++)
    //  {
    //        if (obj[j].checked)
    //            {
    //                 chosen = obj[j].value;
    //            }
    // }
    // if (chosen == null)
    // {
    //        alert("No Delivery Type Chosen");
    //        valid=false;
    //
    // }
	// }
    //
    // if (valid==true){
	//     for (var i = 8; i < (form1.elements.length) -2 ;i++) {
	//     	//To avoid validation for fieldset tags.
	//     	if ((i==15) || (i==19)){
	//     		continue;
	//     	}
    //
	//     	if (i==9){
	//     		var email=form1.elements[i].value;
	//     		var mailformat = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
	// 			if (!(email.match(mailformat))){
	// 			  alert ("Please enter a valid email address.");
	// 	          form1.elements[i].focus();
	// 	          form1.elements[i].select();
	// 	          form1.elements[i].style.backgroundColor="red";
	// 	          valid = false;
	// 	          break;
	// 			}
	//     	}
    //
	//     	if (i==14){
	//     		var zip=form1.elements[i].value;
	//     		if ((zip=="")||(zip==null)||(isNaN(zip))||(zip.length!=5)){
	//     		  alert ("Please enter a valid zip code (5 digits).");
	// 	          form1.elements[i].focus();
	// 	          form1.elements[i].select();
	// 	          form1.elements[i].style.backgroundColor="red";
	// 	          valid = false;
	// 	          break;
	//     		}
    //
	//     	}
    //
	//         if ((form1.elements[i].value == "") || (form1.elements[i].value == null))
	//         {
	//         	if ((i==13) || (i==20)){
	//         		alert ("Please enter a valid value for " + form1.elements[i].name);
	//         		valid = false;
	// 	          	break;
	//         	}
	//         	else{
	// 	          alert ("Please enter a value for " + form1.elements[i].name)
    //
	// 	          form1.elements[i].focus();
	// 	          form1.elements[i].select();
	// 	          form1.elements[i].style.backgroundColor="red";
	// 	          valid = false;
	// 	          break;
	//           	}
    //
	//         }
    //
	//     }
    //
	// }
    //
	// if (valid == true ){
	// 	for (var i = 0; i < (form1.elements.length) -2 ;i++){
    //     	if ((i==0) || (i==7) || (i==15) || (i==19)){
	//     		continue;
	//     	}
    //
	//     	if ((i == 16 ) || (i == 17)){
    //          if (form1.elements[i].checked){
    //             text += form1.elements[i].name + " : " + form1.elements[i].value + "<br>";
    //            }
    //        	} else if ((i == 1 ) || (i == 3) || (i == 4) || (i == 6) || (i == 18) || (i == 24)){
    //        		text += form1.elements[i].name + " : $" + form1.elements[i].value + "<br>";
    //        	} else if ((i == 13 ) || (i == 20)){
    //        		text += form1.elements[i].name + " : " + form1.elements[i].options[form1.elements[i].selectedIndex].value + "<br>";
    //        	} else if (i==21){
    //        		var ccnumber= form1.elements[i].value;
    //        		var ccrepresentation =  "X".repeat(ccnumber.length-4) + ccnumber.slice(ccnumber.length-4);
    //        		text += form1.elements[i].name + " : " + ccrepresentation + "<br>";
    //        	} else{
    //             text += form1.elements[i].name + " : " + form1.elements[i].value + "<br>";
    //        	}
    //     }
    //
	//     var d= new Date();
	//     text += "<br>Today's date is " +  d.toDateString() +".</p>";
	//     document.getElementById('output').innerHTML=text;
    //
	// }
    //


}







