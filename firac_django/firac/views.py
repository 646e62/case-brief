"""
The views file. This file contains the functions that are called when a user 
visits a page.
"""

from django.shortcuts import render, redirect
from .forms import AnalysisForm
from .apps import canlii_html_to_txt, classify_firac, process_json_file, extract_citations, local_text_summary, gpt_hybrid_analysis_manual

def index(request):
    """
    The main index view. This view is called when the user visits the home 
    page. 
    """
    if request.method == 'POST':
        api_key = request.POST.get('api_key', '')
        return render(request, 'index.html', {'api_key': api_key})
    return render(request, 'index.html')


def file_input(request):
    """
    Handles the file input view. This view is called when the user selects the
    file input option. It will take the file and send it to the output view.
    """
    api_key = request.GET.get('api_key', '')
    if request.method == 'POST':
        # Assign the file to a variable
        file = request.FILES['file']
        file_extension = file.name.split('.')[-1]

        # The default file extension will be html or mhtml
        # If it is either of those, the file will need to be converted to txt
        # This can be done using some of the functions in the utils.py file
        if file_extension == 'html' or file_extension == 'mhtml':
            # Convert the file to txt and assign it to a variable
            # Run the file through the applicable CLI functions
            text = canlii_html_to_txt(file)
            firac = classify_firac(text)
#           citations = extract_citations(text)
            summary = local_text_summary(firac)
#           analysis = local_text_analysis(citations)
            report = gpt_hybrid_analysis_manual(summary, api_key)
            request.session['output'] = report

            request.session['output'] = report
            return redirect('output')
        
        elif file_extension == 'txt':
            # Assign the file to a variable
            # Run the file through the applicable CLI functions
            request.session['output'] = "Automatic processing from text is not available yet."           
            return redirect('output')
            
        elif file_extension == 'json':
            firac = process_json_file(file)
            text = ""
            for key in firac:
                text += firac[key]
            citations = extract_citations(text)
            summary = local_text_summary(firac)
 #           analysis = local_text_analysis(citations)
            report = gpt_hybrid_analysis_manual(summary, api_key)
            request.session['output'] = report
            
            return redirect('output')
        else:
            file_extension = "Unknown file extension. Please try again."

        # Return the file extension and have it appear in output.html
        request.session['output'] = file_extension
        return redirect('output')
    return render(request, 'file_input.html', {'api_key': api_key})


def manual_input(request):
    """
    Calls the manual input view and sends the output to the output view.
    """
    api_key = request.GET.get('api_key', '')
    if request.method == 'POST':
        form = AnalysisForm(request.POST)
        if form.is_valid():
            # Call your CLI functions here based on the input data
            output_text = 'Facts:\n\nIssues:\n\nRules:\n\nAnalysis:\n\nConclusion:\n'
            request.session['output'] = output_text
            return redirect('output')
    else:
        form = AnalysisForm()

    return render(request, 'manual_input.html', {'form': form, 'api_key': api_key})


def output(request):
    """
    Receives input from either the manual or automatic input views and displays the output.
    """
    output_data = request.session.get('output', '')
    return render(request, 'output.html', {'output': output_data})
