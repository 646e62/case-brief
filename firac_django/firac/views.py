from django.shortcuts import render
from .forms import AnalysisForm

def index(request):
    export = False

    if request.method == 'POST':
        form = AnalysisForm(request.POST)
        if form.is_valid():
            # Call your CLI functions here based on the file type uploaded
            # Set the output to the form's output field
            output = 'Facts:\nYour output facts\n\nIssues:\nYour output issues\n\nRules:\nYour output rules\n\nAnalysis:\nYour output analysis\n\nConclusion:\nYour output conclusion'
            form.fields['output'].initial = output

            # Make output field editable
            form.fields['output'].widget.attrs.pop('readonly', None)

            export = True
    else:
        form = AnalysisForm()

    return render(request, 'index.html', {'form': form, 'export': export})
