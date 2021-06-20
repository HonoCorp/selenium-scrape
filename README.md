# Scrape Google Maps Using Selenium

This is a simple demo on how to scrape Google Maps using Selenium WebDriver.

## Instructions
Install selenium  
> pip install selenium  

Download the chromedriver that is compatible with your version of chrome browser from [this url](https://chromedriver.storage.googleapis.com/index.html)

Add the chromedriver to your path. For directions on how to add chromedriver to your PATH, go to [selenium website](https://www.selenium.dev/documentation/en/webdriver/driver_requirements/#adding-executables-to-your-path)

Run `app.py` to see usage and available options  
> python app.py  

## Examples
1. Generate links for hotels in Mombasa
```shell  
python app.py -l mombasa -o mombasa-hotels.txt hotel
```

2. Generate links for companies in Nairobi  
```shell
python app.py -l nairobi -o nairobi-companies.txt company
```

3. Process output file after generating links for all companies in Nairobi  
```shell  
python app.py -o nairobi-companies.txt -p company
```  

4. Process given file  
```shell  
python process.py filename.txt
```
