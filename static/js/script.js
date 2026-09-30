document.addEventListener(
    "DOMContentLoaded",
    function () {

        const audioInput =
            document.getElementById("audio");

        const fileName =
            document.getElementById("file-name");

        if (audioInput) {

            audioInput.addEventListener(
                "change",
                function () {

                    if (audioInput.files.length > 0) {

                        fileName.textContent =
                            "Selected: " +
                            audioInput.files[0].name;

                    } else {

                        fileName.textContent =
                            "No file selected";
                    }

                }
            );
        }
    }
);