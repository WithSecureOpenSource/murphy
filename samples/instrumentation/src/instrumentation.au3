#include <GUIConstantsEx.au3>
#include <MsgBoxConstants.au3>
#include <FileConstants.au3>

;
; Simple Installation dialog with a installation folder field
;

func WelcomeDialog()

    Local $hGUI = GUICreate("SuperApp Installer", 470, 240)

    GUISetFont(11)
    Local $iLabel = GUICtrlCreateLabel("Welcome to SuperApp!", 10, 10, 325, 55)
    Local $iLabel2 = GUICtrlCreateLabel("To install superapp please press next.", 10, 55, 325, 55)

    
    GUISetFont(9)
    Local $iCancel = GUICtrlCreateButton("&Cancel", 18, 198, 104, 28)
    Local $iNext = GUICtrlCreateButton("&Next >>", 350, 198, 104, 28)

    ; Display the GUI.
    GUISetState(@SW_SHOW, $hGUI)

    While 1
        Switch GUIGetMsg()
            Case $GUI_EVENT_CLOSE, $iCancel
                Local $answer = MsgBox($MB_OKCANCEL + $MB_ICONQUESTION + $MB_TASKMODAL + $MB_DEFBUTTON2, "Installation", "Are you sure you dont want to install this supper application?")
                if $answer = $IDOK Then
                    GUIDelete($hGUI)
                    Return False
                EndIf
            Case $iNext
                GUIDelete($hGUI)
                Return True
        EndSwitch
    WEnd
    
EndFunc

func Eula()

    Local $hGUI = GUICreate("SuperApp Installer", 470, 240)

    GUISetFont(11)
    Local $iLabel = GUICtrlCreateLabel("Welcome to SuperApp!", 10, 10, 325, 55)
    
    Local $iLabel2 = GUICtrlCreateLabel("License Terms", 10, 45, 325, 55)
    
    GUISetFont(9)
    Local $iCancel = GUICtrlCreateButton("&Cancel", 18, 198, 104, 28)
    Local $iNext = GUICtrlCreateButton("&Next >>", 350, 198, 104, 28)

    ; Display the GUI.
    GUISetState(@SW_SHOW, $hGUI)

    Local $result = InetGet("http://www.google.com", "test.html")
    if $result = 0 Then
        MsgBox($MB_OK + $MB_ICONERROR + $MB_TASKMODAL, "Installation", "Failed to download the terms and conditions, please check your network connectivity and try again.")
        Return False
    EndIf
    
    Local $conditions = GUICtrlCreateLabel("I hereby accept full responsibility for whatever happens whenever happens for whatever I do" & @CRLF & "By pressing next I take all the risks like a grown up.", 10, 70, 450, 60)

    While 1
        Switch GUIGetMsg()
            Case $GUI_EVENT_CLOSE, $iCancel
                Local $answer = MsgBox($MB_OKCANCEL + $MB_ICONQUESTION + $MB_TASKMODAL + $MB_DEFBUTTON2, "Installation", "Are you sure you dont accept our fair and simple license terms?")
                if $answer = $IDOK Then
                    GUIDelete($hGUI)
                    Return False
                EndIf
            Case $iNext
                GUIDelete($hGUI)
                Return True
        EndSwitch
    WEnd
    
EndFunc

func SelectDestination()

    Local $hGUI = GUICreate("SuperApp Installer", 470, 240)

    GUISetFont(11)
    Local $iLabel = GUICtrlCreateLabel("Welcome to SuperApp!", 10, 10, 325, 55)
    
    Local $iLabel2 = GUICtrlCreateLabel("Destination Folder", 10, 85, 325, 55)
    Local $edit = GUICtrlCreateInput("C:\Program Files\Here", 10, 110, 450, 20)
    
    GUISetFont(9)
    Local $iCancel = GUICtrlCreateButton("&Cancel", 18, 198, 104, 28)
    Local $iNext = GUICtrlCreateButton("&Next >>", 350, 198, 104, 28)

    ; Display the GUI.
    GUISetState(@SW_SHOW, $hGUI)

    While 1
        Switch GUIGetMsg()
            Case $GUI_EVENT_CLOSE, $iCancel
                Local $answer = MsgBox($MB_OKCANCEL + $MB_ICONQUESTION + $MB_TASKMODAL + $MB_DEFBUTTON2, "Installation", "Are you sure you want to cancel the installation?")
                if $answer = $IDOK Then
                    GUIDelete($hGUI)
                    Return False
                EndIf
            Case $iNext
                Local $dir = GUICtrlRead($edit)
                GUIDelete($hGUI)
                Return $dir
        EndSwitch
    WEnd
    
EndFunc

func RunSetup()
    if WelcomeDialog() = False Then
        Return
    EndIf
    if Eula() = False Then
        Return
    EndIf
    Local $installation_dir = SelectDestination()
    if $installation_dir = False Then
        Return
    EndIf
    if DirCreate($installation_dir) = 0 Then
        MsgBox($MB_OK + $MB_ICONERROR + $MB_TASKMODAL + $MB_DEFBUTTON2, "Installation", "Failed to create installation directory " & $installation_dir)
    Else
        FileWrite($installation_dir & "\readme.txt", "Hi mr.")
        RegWrite("HKEY_CURRENT_USER\Software\Test", "TestKey", "REG_SZ", "Hello this is a test")
        MsgBox($MB_OK + $MB_TASKMODAL, "Installation", "Installation completed, enjoy!")
    EndIf
    
EndFunc

RunSetup()

    