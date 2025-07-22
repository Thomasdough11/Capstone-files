# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Generate launch site options for dropdown
launch_sites = [{'label': 'All Sites', 'value': 'ALL'}] + \
               [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Launch Site dropdown
    dcc.Dropdown(id='site-dropdown',
                 options=launch_sites,
                 value='ALL',
                 placeholder="Select a Launch Site",
                 searchable=True,
                 style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'textAlign': 'center', 'margin': 'auto'}),
    html.Br(),

    # TASK 2: Success Pie Chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):", style={'textAlign': 'center'}),

    # TASK 3: Payload Range Slider
    dcc.RangeSlider(id='payload-slider',
                    min=min_payload,
                    max=max_payload,
                    step=100,
                    value=[min_payload, max_payload],
                    marks={int(min_payload): str(int(min_payload)),
                           int(max_payload): str(int(max_payload))}),
    
    # TASK 4: Payload vs. Success Scatter Plot
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback for Pie Chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        pie_df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(pie_df, names='Launch Site', title='Total Successful Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        count_df = filtered_df['class'].value_counts().reset_index()
        count_df.columns = ['class', 'count']
        count_df['class'] = count_df['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(count_df, values='count', names='class',
                     title=f'Total Success vs Failure for site {selected_site}')
    return fig

# TASK 4: Callback for Scatter Plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_plot(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                            (spacex_df['Payload Mass (kg)'] <= high)]
    
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(filtered_df,
                     x='Payload Mass (kg)',
                     y='class',
                     color='Booster Version Category',
                     title=f'Success by Payload for {"All Sites" if selected_site == "ALL" else selected_site}',
                     labels={'class': 'Launch Outcome'})
    return fig

# Run the app
if __name__ == '__main__':
    app.run()