function changeForm(id) {
	if(id == "SignForm"){
		document.getElementById("LogForm").style.display == "none";
	} else{
		document.getElementById("SignForm").style.display == "none";
	}

	if(document.getElementById(id).style.display == "none"){
		document.getElementById(id).style.display = "block";
	} else{
		document.getElementById(id).style.display = "none";
	}
}