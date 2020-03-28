// This file is needed by qtinstall.py,
// See: https://doc.qt.io/qtinstallerframework/scripting-qinstaller.html
// Missing the InstallComponents and InstallPath variables
// that will be appended here by the install script.

function Controller() {
    installer.setMessageBoxAutomaticAnswer("OverwriteTargetDirectory", QMessageBox.Ok)
    installer.setMessageBoxAutomaticAnswer("installationError", QMessageBox.Retry);
    installer.setMessageBoxAutomaticAnswer("installationErrorWithRetry", QMessageBox.Retry);
    installer.setMessageBoxAutomaticAnswer("DownloadError", QMessageBox.Retry);
    installer.setMessageBoxAutomaticAnswer("archiveDownloadError", QMessageBox.Retry);
    installer.setMessageBoxAutomaticAnswer("XcodeError", QMessageBox.Ok);

    installer.installationFinished.connect(proceed)
}

function logCurrentPage() {
    var pageName = page().objectName
    var pagePrettyTitle = page().title
    console.log("At page: " + pageName + " ('" + pagePrettyTitle + "')")
}

function page() {
    return gui.currentPageWidget()
}

function proceed(button, delay) {
    gui.clickButton(button || buttons.NextButton, delay)
}

Controller.prototype.WelcomePageCallback = function() {
    logCurrentPage();

    // The installer needs to fetch some stuff.
    page().completeChanged.connect(function() {
        proceed();
    });
}

Controller.prototype.CredentialsPageCallback = function() {
    logCurrentPage();

    page().loginWidget.EmailLineEdit.text ='qtinstallerthrowaway@gmail.com'
    page().loginWidget.PasswordLineEdit.text = 'e6^u5F$E5Tsq'

    proceed()
}

Controller.prototype.ObligationsPageCallback = function() {
    logCurrentPage();

    page().obligationsAgreement.setChecked(true)
    // Needs this, don't know why.
    page().completeChanged();

    proceed()
}

Controller.prototype.IntroductionPageCallback = function() {
    logCurrentPage()

    proceed()
}

Controller.prototype.TargetDirectoryPageCallback = function() {
    logCurrentPage()

    page().TargetDirectoryLineEdit.text = InstallPath

    proceed()
}

Controller.prototype.ComponentSelectionPageCallback = function() {
    logCurrentPage()

    // Deselect whatever was default, and can be deselected.
    page().deselectAll()

    InstallComponents.forEach(component => {
        page().selectComponent(component)
    })

    proceed()
}

Controller.prototype.LicenseAgreementPageCallback = function() {
    logCurrentPage()

    page().AcceptLicenseRadioButton.setChecked(true)

    proceed()
}


// Windows-specific:
Controller.prototype.StartMenuDirectoryPageCallback = function() {
    logCurrentPage()

    proceed()
}

Controller.prototype.ReadyForInstallationPageCallback = function() {
    logCurrentPage()

    proceed()
}

// Installation in progress, do nothing.
Controller.prototype.PerformInstallationPageCallback = function() {
    logCurrentPage()
}

Controller.prototype.FinishedPageCallback = function() {
    logCurrentPage()

    // Deselect "launch QtCreator"
    page().LaunchQtCreatorCheckBoxForm.launchQtCreatorCheckBox.setChecked(false)

    proceed(buttons.FinishButton)
}
