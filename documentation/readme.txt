Linux PHP requires:
	php7.4-cli
	php7.4-curl
	php7.4-sqlite3

CollectAll must run on Linux (or WSL)
ReportAll must run on Windows (for Chrome)


Report JSON file objects documentation

. offline - boolean - <false|true>
	Defines if the report will use online or offline (modded) version of Google Charts.
	If not defined, the default is to use online.
. language - text - <en|de|es|fr|pt_br>
	Specifies the language which will be used for the Google Charts library.
	If not defined, the default is 'en'.
. title - text
	Title which will be used for the report. Becomes the title of the html page.
	If not defined, 'Report v5.0' is used.
. stylesheet - text
	Location of the alternate stylesheet file to be used on the report.
	If not defined, the default.css file will be used.
. defaults - object
	Defines the default elements which will be added to each object.
	. text - object
		Defines which elements will be added to all the text objects.
	. image - object
		Defines which elements will be added to all the image objects.
	. chart - object
		Defines which elements will be added to all the chart objects.
	. variable - object
		Defines which elements will be added to all the variable objects.
	. page - object
		Defines which elements will be added to all pages.
. pages - array of objects
	Contains the definition of each page of the report.
	. landscape - <false|true>
		Defines if the page will be rendered in landscape mode.
	. objects - array of objects
		Contains the definition of each page objects.
		