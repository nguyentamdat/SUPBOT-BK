const defaultBtn = document.querySelector("#default-image-btn");

defaultBtn.addEventListener("change", function (event) {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function () {
            const result = reader.result;
            Botkit.sendImage(result, event);
        };
        reader.readAsDataURL(file);
    }
});
