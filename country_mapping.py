"""Country to Continent and Regional Block Mapping"""

# Continent Mapping
CONTINENT_MAP = {
    # Africa
    'Algeria': 'AFRICA', 'Angola': 'AFRICA', 'Benin': 'AFRICA', 'Botswana': 'AFRICA',
    'Burkina Faso': 'AFRICA', 'Burundi': 'AFRICA', 'Cameroon': 'AFRICA', 'Cape Verde': 'AFRICA',
    'Central African Republic': 'AFRICA', 'Chad': 'AFRICA', 'Comoros': 'AFRICA',
    'Congo': 'AFRICA', 'Congo, The Democratic Republic Of': 'AFRICA', "Cote D'Ivoire": 'AFRICA',
    'Djibouti': 'AFRICA', 'Egypt': 'AFRICA', 'Equatorial Guinea': 'AFRICA', 'Eritrea': 'AFRICA',
    'Ethiopia': 'AFRICA', 'Gabon': 'AFRICA', 'Gambia': 'AFRICA', 'Ghana': 'AFRICA',
    'Guinea': 'AFRICA', 'Guinea-Bissau': 'AFRICA', 'Kenya': 'AFRICA', 'Lesotho': 'AFRICA',
    'Liberia': 'AFRICA', 'Libya': 'AFRICA', 'Madagascar': 'AFRICA', 'Malawi': 'AFRICA',
    'Mali': 'AFRICA', 'Mauritania': 'AFRICA', 'Mauritius': 'AFRICA', 'Morocco': 'AFRICA',
    'Mozambique': 'AFRICA', 'Namibia': 'AFRICA', 'Niger': 'AFRICA', 'Nigeria': 'AFRICA',
    'Rwanda': 'AFRICA', 'Sao Tome And Principe': 'AFRICA', 'Senegal': 'AFRICA',
    'Seychelles': 'AFRICA', 'Sierra Leone': 'AFRICA', 'Somalia': 'AFRICA', 'South Africa': 'AFRICA',
    'South Sudan': 'AFRICA', 'Sudan': 'AFRICA', 'Swaziland': 'AFRICA', 'Tanzania': 'AFRICA',
    'Togo': 'AFRICA', 'Tunisia': 'AFRICA', 'Uganda': 'AFRICA', 'Zambia': 'AFRICA', 'Zimbabwe': 'AFRICA',
    
    # America
    'United States': 'AMERICA', 'Canada': 'AMERICA', 'Mexico': 'AMERICA', 'Brazil': 'AMERICA',
    'Argentina': 'AMERICA', 'Chile': 'AMERICA', 'Colombia': 'AMERICA', 'Peru': 'AMERICA',
    'Venezuela': 'AMERICA', 'Ecuador': 'AMERICA', 'Bolivia': 'AMERICA', 'Paraguay': 'AMERICA',
    'Uruguay': 'AMERICA', 'Guyana': 'AMERICA', 'Suriname': 'AMERICA', 'Jamaica': 'AMERICA',
    'Trinidad And Tobago': 'AMERICA', 'Bahamas': 'AMERICA', 'Barbados': 'AMERICA',
    'Costa Rica': 'AMERICA', 'Panama': 'AMERICA', 'Guatemala': 'AMERICA', 'Honduras': 'AMERICA',
    'Nicaragua': 'AMERICA', 'El Salvador': 'AMERICA', 'Cuba': 'AMERICA', 'Haiti': 'AMERICA',
    'Dominican Republic': 'AMERICA',
    
    # Asia
    'China': 'ASIA', 'India': 'ASIA', 'Japan': 'ASIA', 'South Korea': 'ASIA', 'Indonesia': 'ASIA',
    'Pakistan': 'ASIA', 'Bangladesh': 'ASIA', 'Vietnam': 'ASIA', 'Thailand': 'ASIA',
    'Myanmar': 'ASIA', 'Philippines': 'ASIA', 'Afghanistan': 'ASIA', 'Nepal': 'ASIA',
    'Sri Lanka': 'ASIA', 'Malaysia': 'ASIA', 'Singapore': 'ASIA', 'Cambodia': 'ASIA',
    'Laos': 'ASIA', 'Mongolia': 'ASIA', 'Brunei': 'ASIA', 'Bhutan': 'ASIA', 'Maldives': 'ASIA',
    'Saudi Arabia': 'ASIA', 'United Arab Emirates': 'ASIA', 'Iran': 'ASIA', 'Iraq': 'ASIA',
    'Israel': 'ASIA', 'Jordan': 'ASIA', 'Kuwait': 'ASIA', 'Lebanon': 'ASIA', 'Oman': 'ASIA',
    'Qatar': 'ASIA', 'Yemen': 'ASIA', 'Bahrain': 'ASIA', 'Palestine': 'ASIA', 'Syria': 'ASIA',
    'Turkey': 'ASIA', 'Armenia': 'ASIA', 'Azerbaijan': 'ASIA', 'Georgia': 'ASIA',
    'Kazakhstan': 'ASIA', 'Kyrgyzstan': 'ASIA', 'Tajikistan': 'ASIA', 'Turkmenistan': 'ASIA',
    'Uzbekistan': 'ASIA',
    
    # Europe
    'United Kingdom': 'EUROPE', 'Germany': 'EUROPE', 'France': 'EUROPE', 'Italy': 'EUROPE',
    'Spain': 'EUROPE', 'Poland': 'EUROPE', 'Romania': 'EUROPE', 'Netherlands': 'EUROPE',
    'Belgium': 'EUROPE', 'Greece': 'EUROPE', 'Portugal': 'EUROPE', 'Czech Republic': 'EUROPE',
    'Hungary': 'EUROPE', 'Sweden': 'EUROPE', 'Austria': 'EUROPE', 'Bulgaria': 'EUROPE',
    'Denmark': 'EUROPE', 'Finland': 'EUROPE', 'Slovakia': 'EUROPE', 'Norway': 'EUROPE',
    'Ireland': 'EUROPE', 'Croatia': 'EUROPE', 'Switzerland': 'EUROPE', 'Serbia': 'EUROPE',
    'Lithuania': 'EUROPE', 'Slovenia': 'EUROPE', 'Latvia': 'EUROPE', 'Estonia': 'EUROPE',
    'Albania': 'EUROPE', 'Moldova': 'EUROPE', 'Bosnia And Herzegovina': 'EUROPE',
    'North Macedonia': 'EUROPE', 'Iceland': 'EUROPE', 'Luxembourg': 'EUROPE', 'Malta': 'EUROPE',
    'Montenegro': 'EUROPE', 'Cyprus': 'EUROPE', 'Russia': 'EUROPE', 'Ukraine': 'EUROPE',
    'Belarus': 'EUROPE',
    
    # Oceania
    'Australia': 'OCEANIA', 'New Zealand': 'OCEANIA', 'Papua New Guinea': 'OCEANIA',
    'Fiji': 'OCEANIA', 'Solomon Islands': 'OCEANIA', 'Vanuatu': 'OCEANIA', 'Samoa': 'OCEANIA',
}

# Regional Blocks
EAC_COUNTRIES = ['Burundi', 'Kenya', 'South Sudan', 'Tanzania', 'Congo, The Democratic Republic Of', 'Somalia', 'Uganda']
EAC_PARTNER_STATES = ['Burundi', 'Kenya', 'South Sudan', 'Tanzania', 'Uganda']

COMESA_COUNTRIES = ['Burundi', 'Comoros', 'Congo, The Democratic Republic Of', 'Djibouti', 'Egypt',
                    'Eritrea', 'Ethiopia', 'Kenya', 'Libya', 'Madagascar', 'Malawi', 'Mauritius',
                    'Rwanda', 'Seychelles', 'Somalia', 'Sudan', 'Swaziland', 'Uganda', 'Zambia', 'Zimbabwe']

SADC_COUNTRIES = ['Angola', 'Botswana', 'Comoros', 'Congo, The Democratic Republic Of', 'Lesotho',
                  'Madagascar', 'Malawi', 'Mauritius', 'Mozambique', 'Namibia', 'Seychelles',
                  'South Africa', 'Swaziland', 'Tanzania', 'Zambia', 'Zimbabwe']

ECOWAS_COUNTRIES = ['Benin', 'Burkina Faso', 'Cape Verde', "Cote D'Ivoire", 'Gambia', 'Ghana',
                    'Guinea', 'Guinea-Bissau', 'Liberia', 'Mali', 'Niger', 'Nigeria', 'Senegal',
                    'Sierra Leone', 'Togo']

CEPGL_COUNTRIES = ['Burundi', 'Congo, The Democratic Republic Of', 'Rwanda']

COMMONWEALTH_COUNTRIES = ['Antigua And Barbuda', 'Australia', 'Bahamas', 'Bangladesh', 'Barbados',
                         'Belize', 'Botswana', 'Brunei', 'Cameroon', 'Canada', 'Cyprus', 'Dominica',
                         'Fiji', 'Gambia', 'Ghana', 'Grenada', 'Guyana', 'India', 'Jamaica', 'Kenya',
                         'Lesotho', 'Malawi', 'Malaysia', 'Maldives', 'Malta', 'Mauritius', 'Mozambique',
                         'Namibia', 'New Zealand', 'Nigeria', 'Pakistan', 'Papua New Guinea', 'Rwanda',
                         'Saint Lucia', 'Samoa', 'Seychelles', 'Sierra Leone', 'Singapore', 'Solomon Islands',
                         'South Africa', 'Sri Lanka', 'Swaziland', 'Tanzania', 'Tonga', 'Trinidad And Tobago',
                         'Uganda', 'United Kingdom', 'Vanuatu', 'Zambia']

EU_COUNTRIES = ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark',
                'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy',
                'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands', 'Poland', 'Portugal',
                'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden']

def get_continent(country):
    """Get continent for a country"""
    return CONTINENT_MAP.get(country, 'OTHER')

def get_regional_blocks(country):
    """Get all regional blocks a country belongs to"""
    blocks = []
    if country in EAC_COUNTRIES:
        blocks.append('EAC')
    if country in COMESA_COUNTRIES:
        blocks.append('COMESA')
    if country in SADC_COUNTRIES:
        blocks.append('SADC')
    if country in ECOWAS_COUNTRIES:
        blocks.append('ECOWAS')
    if country in CEPGL_COUNTRIES:
        blocks.append('CEPGL')
    if country in COMMONWEALTH_COUNTRIES:
        blocks.append('COMMONWEALTH')
    if country in EU_COUNTRIES:
        blocks.append('EU')
    return blocks