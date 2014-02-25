#include <Constants.au3>

;
; Simple Installation dialog with a serial number / installation key prompt
;

Local $sText = ""
While True
    $sText = InputBox("Welcome to superapp", "Please type in your installation key and click OK", "", "", 280, 140)
    If @error = 1 Then
        MsgBox($MB_SYSTEMMODAL, "Bye", "We're sorry you did not installed us.")
        ExitLoop
    Else
        If $sText = "demo" Then
            MsgBox($MB_SYSTEMMODAL, "Demo installation", "Thans for installing our demo version!")
            ExitLoop
        ElseIf $sText = "full" Then ; This is not case-sensitive
            MsgBox($MB_SYSTEMMODAL, "Full installation", "Thans for installing our full version!")
            ExitLoop
        Else
            MsgBox($MB_SYSTEMMODAL, "Error", "Invalid key, please try again!")
        EndIf
    EndIf
WEnd
