from pprint import pformat
import pyodide.http
from shiny import App, reactive, render, ui
#CHOIX A ETENDRE CELON CE DONT ON A BESOIN
choices_synop= "date","nom","pres","vv"
condition_filtres_synop = 'nom="MONTPELLIER"','year(date)="2017"'
choices_atmos="nom_poll","nom_com","date_debut","date_fin","valeur"
condition_filtres_atmos="nom_poll='O3'","nom_poll='NO2'"

app_ui = ui.page_fluid(
    ui.input_selectize("selection", "Selection_synop", choices_synop, multiple = True),
    ui.input_selectize("condition", "Condition", condition_filtres_synop, multiple = True),
    ui.input_selectize("ordonné", "ordonné par", choices_synop, multiple = True),
    ui.output_text_verbatim("info"),
    ui.input_selectize("selection1", "Selection_atmos", choices_atmos, multiple = True),
    ui.input_selectize("condition1", "Condition", condition_filtres_atmos, multiple = True),
    ui.input_date("date","à partir de"),
    ui.output_text_verbatim("info1"),
)

def server(input, output, session):
    @reactive.Calc
    def url():
        select = ','.join(input.selection())
        cond = "&where="+ 'and '.join(input.condition())
        ordo="&order_by="+ ','.join(input.ordonné())
        return f"https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/donnees-synop-essentielles-omm/records?select={select}{cond}{ordo}"
    def url1():
        select1 = "&outFields="+ ','.join(input.selection1())
        cond1 = "where=("+ ') AND ('.join(input.condition1())+')'
        date1= f"AND (date_debut >= '{input.date()}"+" 00:00:00' )"
        return f"https://services9.arcgis.com/7Sr9Ek9c1QTKmbwr/arcgis/rest/services/mesures_occitanie_72h_poll_princ/FeatureServer/0/query?{cond1}{date1}{select1}&f=json"

    @reactive.Calc
    async def data():
        response = await pyodide.http.pyfetch(url())
        response1 = await pyodide.http.pyfetch(url1())
        dat = await response.json()
        dat1 = await response1.json()
        r= dat,dat1
        return r

    @output
    @render.text
    async def info():
        if input.selection() == "":
            return ""
        else:
            d=await data()
            data_str = pformat(d[0])
            return f"Request URL: {url()}\nResult type: {type(data())}\n{data_str}"
    @output
    @render.text
    async def info1():
        if input.selection1() == "":
            return ""
        else:
            d=await data()
            data_str = pformat(d[1])
            return f"Request URL: {url1()}\nResult type: {type(data())}\n{data_str}"

app = App(app_ui, server)
