window.onload = (event) => {
    const boxElement = document.getElementById("box");
    const dataListElement = document.getElementById("suggestion");
    let keyUpTimer;

    const KEY_UP_DELAY = 100;
    const SERVER_URI = "http://127.0.0.1:8000"

    const updateSuggestions = async () => {
        const boxValue = boxElement.value;

        const params = new URLSearchParams({
            q: boxValue
        });

        const response = await fetch(`${SERVER_URI}/autocomplete?${params}`, {
            method: "POST"
        });
        const responseJson = await response.json();

        dataListOptions = responseJson.suggestions.map((suggestion) => {
            const option = document.createElement('option');
            option.value = suggestion;
            return option;
        })

        dataListElement.replaceChildren(...dataListOptions);
    };

    boxElement.onkeyup = async (event) => {
        clearTimeout(keyUpTimer);
        keyUpTimer = setTimeout(async () => {
            await updateSuggestions();
        }, KEY_UP_DELAY);
    };
};