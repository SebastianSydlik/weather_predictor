with 

source as (

    select * from {{ source('staging', 'table0') }}

),

renamed as (

    select
        date,
        temperature_2m,
        relative_humidity_2m,
        precipitation,
        weather_code,
        cloud_cover,
        wind_speed_100m,
        {{ get_weathercode_description("weather_code") }} as weathercode_description
    from source

)

select * from renamed