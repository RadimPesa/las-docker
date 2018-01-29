function setLoginFocus()
{
if(!formInUse) {
        if (document.getElementById('id_barcode'))
                document.loginForm.username.focus();
        }
}
