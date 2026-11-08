let wordlists;

async function loadData() {
  try {
    const response = await fetch('./wordlists.json'); // Path to your JSON file
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    wordlists = await response.json(); // Parses JSON into a native JS object
    //console.log(wordlists);
  } catch (error) {
    console.error("Could not load JSON:", error);
  }
}

function choice(listname) {
  let randDecimalNum = Math.random() * listname.length;
  let randIntNum = Math.floor(randDecimalNum);
  return listname[randIntNum];
}

function shuffle(array) {
  let currentIndex = array.length;
  while (currentIndex != 0) {
    let randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex--;
    [array[currentIndex], array[randomIndex]] = [
      array[randomIndex], array[currentIndex]];
  }
}

function capitalize(mystr){
  return mystr.substring(0,1).toUpperCase() + mystr.substring(1);
}

function generate() {
  resultDisplay.innerHTML = "";
  for (let i = 0; i < 10; i++) {
    let result = "";
    let categories = ["opinion", "size", "quality", "age", "shape", "color", "origin", "material", "purpose"];
    shuffle(categories);
    limitedCategories = categories.slice(0, numWords.value - 1);
    for (const each of categories) {
      if (limitedCategories.includes(each)) {
        // result += choice(wordlists[each]) + " "
        result += capitalize(choice(wordlists[each]));
      }
    }
    result += capitalize(choice(wordlists["noun"][vocablistDropdown.value])).replaceAll(/\s/g, "").replaceAll("-","");
    resultDisplay.innerHTML += result + "<br>"
  }



}

loadData();