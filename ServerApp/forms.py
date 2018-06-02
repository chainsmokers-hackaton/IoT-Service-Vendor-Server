from django import forms
import json

class AlertForm(forms.Form) :
    alert = forms.CharField(max_length=2024)

    def alert_json(self):
        jdata = self.cleaned_data['alert']
        try:
            json_data = json.loads(jdata)  # loads string as json
            # validate json_data
        except:
            raise forms.ValidationError("Invalid data in jsonfield")
            # if json data not valid:
            # raise forms.ValidationError("Invalid data in jsonfield")
        return jdata