import plugintypes
import urllib
import json


class NutritionPlugin(plugintypes.TelegramPlugin):
    patterns = [
        "^!nutr (.*)"
    ]

    usage = [
        "!nutr <foods>: Get nutrition info",
    ]

    def activate_plugin(self):
        if not self.has_option("api id"):
            self.write_option("api id", "")
        if not self.has_option("api key"):
            self.write_option("api key", "")

    def run(self, msg, matches):
        if self.read_option("api id") == "":
            return "API information not set in plugins.conf, Get them from https://developer.nutritionix.com/"
        url = 'https://apibeta.nutritionix.com/v2/natural'
        headers = {
                "X-APP-ID": self.read_option("api id"),
                "X-APP-KEY": self.read_option("api key"),
                "Content-Type": "text/plain"
        }
        data = matches.group(1).encode('utf-8')

        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req) as response:
                jdata = json.loads(response.read().decode('utf-8'))

                nutrition = { nutr['usda_tag']: "{:.2f} {}".format(nutr['value'], nutr['unit']) for nutr in
                    jdata['total']['nutrients'] }

                return '{name} ({weight} g): {kcal}, Fat: {fat} (PUF: {puf}, MUF: {mf}, SF: {sf}), Protein: {protein}\n Total Carbs: {carbs}, Sugar: {sugar}, Fiber: {fiber}'.format(
                    name=matches.group(1),
                    kcal=nutrition['ENERC_KCAL'],
                    weight=jdata['total']['serving_weight_grams'],
                    fat=nutrition['FAT'],
                    puf=nutrition['FAPU'],
                    mf=nutrition['FAMS'],
                    sf=nutrition['FASAT'],
                    protein=nutrition['PROCNT'],
                    carbs=nutrition['CHOCDF'],
                    sugar=nutrition['SUGAR'],
                    fiber=nutrition['FIBTG'],
                )
        except urllib.error.HTTPError as err:
            jerr = json.loads(err.read().decode('utf-8'))
            return "Error looking up food: {}".format(jerr['errors'][0]['message'])
