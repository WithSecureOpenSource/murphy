#include <GUIConstantsEx.au3>
#include <MsgBoxConstants.au3>

; Simple installation dialog with option for minimal and full install.
; The next button is disabled until installation type is selected by the user
; Each type of installation finishes with a different message

func WelcomeDialog()

    Local $hGUI = GUICreate("SuperApp Installer", 670, 440)

    Local $iLabel = GUICtrlCreateLabel("Please select type of installation", 10, 10, 185, 25)

    Local $iFull = GUICtrlCreateRadio ( "Full, the product will install all it's components", 10, 40 , 260, 30)
    Local $iPartial = GUICtrlCreateRadio ( "Minimal, only the core components", 10, 70 , 260, 30)
    
    Local $iCancel = GUICtrlCreateButton("&Cancel", 28, 398, 104, 28)
    Local $iNext = GUICtrlCreateButton("&Next", 540, 398, 104, 28)

    GUICtrlSetState($iNext, $GUI_DISABLE) 

    ; Display the GUI.
    GUISetState(@SW_SHOW, $hGUI)

    Local $installFull = True
    
    While 1
        Switch GUIGetMsg()
            Case $GUI_EVENT_CLOSE, $iCancel
                ExitLoop
            Case $iFull
                $installFull = True
                GUICtrlSetState($iNext, $GUI_ENABLE)
            Case $iPartial
                $installFull = False
                GUICtrlSetState($iNext, $GUI_ENABLE)
            Case $iNext
                If $installFull = True Then
                    MsgBox($MB_SYSTEMMODAL, "Installation completed", "Installation is completed for the full product.")
                Else
                    MsgBox($MB_SYSTEMMODAL, "Installation completed", "Installation is completed, only the core modules were installed.")
                EndIf
                ExitLoop
        EndSwitch
    WEnd
    
EndFunc

WelcomeDialog()
