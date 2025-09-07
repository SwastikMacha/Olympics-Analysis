import numpy as np

# Function to fetch medal tally based on selected year and country
def fetch_medal_tally(df, year, country):
    # Remove duplicate entries for same medal to avoid double-counting
    medal_df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    flag = 0

    # Case 1: Both year and country = Overall
    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df

    # Case 2: Year = Overall but country is specified
    if year == 'Overall' and country != 'Overall':
        flag = 1
        temp_df = medal_df[medal_df['region'] == country]

    # Case 3: Specific year but country = Overall
    if year != 'Overall' and country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]

    # Case 4: Both year and country specified
    if year != 'Overall' and country != 'Overall':
        temp_df = medal_df[(medal_df['Year'] == year) & (medal_df['region'] == country)]

    # Grouping logic based on flag
    if flag == 1:  # Show trend over years for a single country
        x = temp_df.groupby('Year').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Year').reset_index()
    else:  # Show medal tally per country
        x = temp_df.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold',
                                                                                      ascending=False).reset_index()

    # Add total medals column
    x['total'] = x['Gold'] + x['Silver'] + x['Bronze']

    # Ensure integer type for medal counts
    x['Gold'] = x['Gold'].astype('int')
    x['Silver'] = x['Silver'].astype('int')
    x['Bronze'] = x['Bronze'].astype('int')
    x['total'] = x['total'].astype('int')

    return x


# Function to get overall medal tally across all years
def medal_tally(df):
    # Remove duplicate medals
    medal_tally = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    # Group by country/region
    medal_tally = medal_tally.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold',
                                                                                                ascending=False).reset_index()
    # Add total medals
    medal_tally['total'] = medal_tally['Gold'] + medal_tally['Silver'] + medal_tally['Bronze']

    # Convert to integers
    medal_tally['Gold'] = medal_tally['Gold'].astype('int')
    medal_tally['Silver'] = medal_tally['Silver'].astype('int')
    medal_tally['Bronze'] = medal_tally['Bronze'].astype('int')
    medal_tally['total'] = medal_tally['total'].astype('int')
    return medal_tally


# Function to get list of years and countries for dropdowns
def country_year_list(df):
    # Unique years list
    years = df['Year'].unique().tolist()
    years.sort()
    years.insert(0, 'Overall')  # Add "Overall" option at beginning

    # Unique countries list
    country = np.unique(df['region'].dropna().values).tolist()
    country.sort()
    country.insert(0, 'Overall')

    return years, country


# Function to compute data trend over time for a given column (e.g., Nations, Events)
def data_over_time(df, col):
    nations_over_time = (
        df.drop_duplicates(['Year', col])['Year']
        .value_counts()  # Count occurrences per year
        .reset_index(name='Count')
        .rename(columns={'index': 'Year'})
        .sort_values('Year')
    )
    return nations_over_time


# Function to find most successful athletes overall or in a specific sport
def most_successful(df, sport):
    # Keep only rows with medals
    temp_df = df.dropna(subset=['Medal'])

    # Filter by sport if not 'Overall'
    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    # Count medals per athlete
    top_athletes = temp_df['Name'].value_counts().reset_index()
    top_athletes.columns = ['Name', 'Medals']  # Rename columns for clarity

    # Get top 15 athletes
    top_athletes = top_athletes.head(15)

    # Merge to get additional athlete info (Sport, Region)
    merged_df = top_athletes.merge(df, on='Name', how='left')

    # Select and clean up columns
    x = merged_df[['Name', 'Medals', 'Sport', 'region']].drop_duplicates('Name')

    return x


# Function to get medal tally year-wise for a specific country
def yearwise_medal_tally(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'], inplace=True)

    # Filter for given country
    new_df = temp_df[temp_df['region'] == country]
    # Count medals year-wise
    final_df = new_df.groupby('Year').count()['Medal'].reset_index()

    return final_df


# Function to create a heatmap (pivot table) for country's performance across sports and years
def country_event_heatmap(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'], inplace=True)

    new_df = temp_df[temp_df['region'] == country]

    # Pivot table: Sports (rows) x Years (columns)
    pt = new_df.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0)
    return pt


# Function to get most successful athletes for a given country
def most_successful_countrywise(df, country):
    # Filter out entries without medals
    temp_df = df.dropna(subset=['Medal'])

    # Filter to the selected country
    temp_df = temp_df[temp_df['region'] == country]

    # Count top 10 athletes by name
    top_athletes = temp_df['Name'].value_counts().reset_index().head(10)
    top_athletes.columns = ['Name', 'Medals']  # Rename columns for clarity

    # Merge to get additional details (e.g., sport)
    merged_df = top_athletes.merge(df, on='Name', how='left')

    # Keep only relevant columns and remove duplicates
    x = merged_df[['Name', 'Medals', 'Sport']].drop_duplicates('Name')

    return x


# Function to analyze Weight vs Height distribution for athletes in a given sport
def weight_v_height(df, sport):
    # Remove duplicate athletes (keep unique Name + region)
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    # Replace NaN in medals with "No Medal"
    athlete_df['Medal'].fillna('No Medal', inplace=True)

    # If sport selected, filter data
    if sport != 'Overall':
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        return temp_df
    else:
        return athlete_df


# Function to compare number of male vs female athletes over years
def men_vs_women(df):
    # Remove duplicate athletes
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    # Count males per year
    men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
    # Count females per year
    women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()

    # Merge results
    final = men.merge(women, on='Year', how='left')
    final.rename(columns={'Name_x': 'Male', 'Name_y': 'Female'}, inplace=True)

    # Fill missing values (if no female athletes in a year)
    final.fillna(0, inplace=True)

    return final
