{#
This macro returns the description from the weather code.
#}

{% macro get_weathercode_description(weather_code) -%}

    case {{ dbt.safe_cast("weather_code", api.Column.translate_type("integer")) }}  
        when 0, then	'Clear sky'
        when 1, then	'Mainly clear'
        when 2, then	'Partly cloudy'
        when 3, then	'Overcast'
        when 45, 48, then	'Fog'
        when 51, 53, 55, 56,57 then	'Drizzle'
        when 61, 63, 65, 80, 81, 82 then	'Rain'
        when 66, 67, then	'Freezing Rain'
        when 71, 73, 75, 77, 85, 86 then	'Snow fall'
        when 95, 96, 99, then	'Thunderstorm'
        else 'EMPTY'
    end

{%- endmacro %}