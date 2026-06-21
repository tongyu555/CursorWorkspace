-- from 吉林
set spark.sql.legacy.timeParserPolicy=LEGACY;
use hsdlake;
cache table ods_5gdpi_step0 as
select
msisdn
,nodebid
,cellid
,time1
,starttime
,endtime
,web_url
,case when coordinate_id=1 then ROUND((SQRT((lon - 0.0065) * (lon - 0.0065) + (lat - 0.006) * (lat - 0.006)) + 0.00002 * SIN((lat - 0.006) * 3.14159265358979324 * 3000.0 / 180.0) )* COS(ATAN2((lat - 0.006), (lon - 0.0065)) + 0.000003 * COS((lon - 0.0065) * 3.14159265358979324 * 3000.0 / 180.0)),6)
        when coordinate_id=2 then lon * 2 -(lon +
                                                    (((300.0 + (lon - 105.0) + 2.0 * (lat - 35.0) + 0.1 * (lon - 105.0) * (lon - 105.0) +
                                                    0.1 * (lon - 105.0) * (lat - 35.0) + 0.1 * sqrt(abs((lon - 105.0))) +
                                                    (20.0 * sin(6.0 * (lon - 105.0) * 3.1415926535897932384626) + 20.0 * sin(2.0 * (lon - 105.0) * 3.1415926535897932384626)) * 2.0 / 3.0 +
                                                    (20.0 * sin((lon - 105.0) * 3.1415926535897932384626) + 40.0 * sin((lon - 105.0) / 3.0 * 3.1415926535897932384626)) * 2.0 / 3.0 +
                                                    (150.0 * sin((lon - 105.0) / 12.0 * 3.1415926535897932384626) + 300.0 * sin((lon - 105.0) / 30.0 * 3.1415926535897932384626)) * 2.0 / 3.0) * 180.0) / (6378245.0 / (SQRT(1 - 0.00669342162296594323 * sin((lat) / 180.0 * 3.1415926535897932384626) * sin((lat) /180.0 * 3.1415926535897932384626))) * COS((lat) / 180.0 * 3.1415926535897932384626) * 3.1415926535897932384626)))
        when coordinate_id=3 then lon end as lon
,case when coordinate_id=1 then ROUND((SQRT((lon - 0.0065) * (lon - 0.0065) + (lat - 0.006) * (lat - 0.006)) + 0.00002 * SIN((lat - 0.006) * 3.14159265358979324 * 3000.0 / 180.0) )
                                        * SIN(ATAN2((lat - 0.006), (lon - 0.0065)) + 0.000003 * COS((lon - 0.0065) * 3.14159265358979324 * 3000.0 / 180.0)),6)
        when coordinate_id=2 then  lat * 2 - (lat +
                                ((-100.0 + 2.0 * (lon - 105.0) + 3.0 * (lat - 35.0) + 0.2 * (lat - 35.0) * (lat - 35.0) +
                                0.1 * (lon - 105.0) * (lat - 35.0) + 0.2 * sqrt(abs(lon - 105.0)) +
                                (20.0 * sin(6.0 * (lon - 105.0) * 3.1415926535897932384626) + 20.0 * sin(2.0 * (lon - 105.0) * 3.1415926535897932384626)) * 2.0/3.0 +
                                (20.0 * sin((lat - 35.0) * 3.1415926535897932384626) + 40.0 * sin((lat - 35.0) / 3.0 * 3.1415926535897932384626)) * 2.0 / 3.0 +
                                (160.0 * sin((lat - 35.0) / 12.0 * 3.1415926535897932384626) + 320 * sin((lat - 35.0) * 3.1415926535897932384626 / 30.0)) * 2.0/ 3.0 ) * 180) / ((6378245.0 * (1 - 0.00669342162296594323)) / ((1 - 0.00669342162296594323 * sin((lat) /180.0 * 3.1415926535897932384626) * sin((lat) /180.0 *3.1415926535897932384626)) * (SQRT(1 - 0.00669342162296594323 * sin((lat) /180.0 * 3.1415926535897932384626) * sin((lat) /180.0 * 3.1415926535897932384626)))) * 3.1415926535897932384626))
        when coordinate_id=3 then lat end as lat
,coordinate_id
,longitude
,latitude
,freq
from
(select
    msisdn
    ,cast((substr(ncgi_ecgi,6)/4096) as bigint) as nodebid
    ,cast((substr(ncgi_ecgi,6)%4096) as bigint) as cellid
    ,unix_timestamp(starttime,'yyyyMMddHHmmss') as time1
    ,cast(from_unixtime(unix_timestamp(starttime,'yyyyMMddHHmmss'),'yyyy-MM-dd HH:mm:ss') as TIMESTAMP) as starttime
    ,cast(from_unixtime(unix_timestamp(endtime,'yyyyMMddHHmmss'),'yyyy-MM-dd HH:mm:ss') as TIMESTAMP) as endtime
    ,regexp_extract(destination_url,'12\\d\\.\\d{4,}|13\\d\\.\\d{4,}',0) as lon
    ,regexp_extract(destination_url,'4\\d\\.\\d{4,}',0) as lat
    ,split(destination_url,'/')[2] as web_url
from ods_5gdpi_http_e2e_telecom_origin_q
where     p_provincecode = 220000 and
    p_date = '2026-03-02' and
    p_hour = 5
and interface=100
and cast(regexp_extract(destination_url,'12\\d\\.\\d{4,}|13\\d\\.\\d{4,}',0) as  int ) > 0
and cast(regexp_extract(destination_url,'4\\d\\.\\d{4,}',0) as int)>0
)a
inner join
cfg_url_coordinate b
on a.web_url=b.url
inner join
(select
        cellkey
        ,cell_longitude as longitude
        ,cell_latitude as latitude
        ,freq
    from fact_nr_cm_projdata
    -- where city='扬州'
)c
on concat(a.nodebid,'_',a.cellid)=c.cellkey;



cache table ods_5gdpi_step1 as
select
     msisdn
    ,nodebid
    ,cellid
    ,time1
    ,starttime
    ,endtime
    ,lon
    ,lat
    ,web_url
    ,round(6378137.0 * acos(sin(lat / 180 * pi()) * sin(latitude / 180 * pi()) + cos(lat / 180 * pi())* cos(latitude / 180 * pi()) *cos((lon - longitude) / 180* pi()))) as dis
    ,freq
from
    (select
         msisdn
        ,nodebid
        ,cellid
        ,time1
        ,starttime
        ,endtime
        ,web_url
        ,case when coordinate_id=1 then lon * 2 -(lon +
                                                         (((300.0 + (lon - 105.0) + 2.0 * (lat - 35.0) + 0.1 * (lon - 105.0) * (lon - 105.0) +
                                                         0.1 * (lon - 105.0) * (lat - 35.0) + 0.1 * sqrt(abs((lon - 105.0))) +
                                                         (20.0 * sin(6.0 * (lon - 105.0) * 3.1415926535897932384626) + 20.0 * sin(2.0 * (lon - 105.0) * 3.1415926535897932384626)) * 2.0 / 3.0 +
                                                         (20.0 * sin((lon - 105.0) * 3.1415926535897932384626) + 40.0 * sin((lon - 105.0) / 3.0 * 3.1415926535897932384626)) * 2.0 / 3.0 +
                                                         (150.0 * sin((lon - 105.0) / 12.0 * 3.1415926535897932384626) + 300.0 * sin((lon - 105.0) / 30.0 * 3.1415926535897932384626)) * 2.0 / 3.0) * 180.0) / (6378245.0 / (SQRT(1 - 0.00669342162296594323 * sin((lat) / 180.0 * 3.1415926535897932384626) * sin((lat) /180.0* 3.1415926535897932384626))) * COS((lat) / 180.0 * 3.1415926535897932384626) * 3.1415926535897932384626)))
              else lon end as lon
        ,case when coordinate_id=1 then lat * 2 - (lat +
                                        ((-100.0 + 2.0 * (lon - 105.0) + 3.0 * (lat - 35.0) + 0.2 * (lat - 35.0) * (lat - 35.0) +
                                        0.1 * (lon - 105.0) * (lat - 35.0) + 0.2 * sqrt(abs(lon - 105.0)) +
                                        (20.0 * sin(6.0 * (lon - 105.0) * 3.1415926535897932384626) + 20.0 * sin(2.0 * (lon - 105.0) * 3.1415926535897932384626)) * 2.0 /3.0 +
                                        (20.0 * sin((lat - 35.0) * 3.1415926535897932384626) + 40.0 * sin((lat - 35.0) / 3.0 * 3.1415926535897932384626)) * 2.0/ 3.0 +
                                        (160.0 * sin((lat - 35.0) / 12.0 * 3.1415926535897932384626) + 320 * sin((lat - 35.0) * 3.1415926535897932384626 / 30.0)) * 2.0 / 3.0 ) * 180) / ((6378245.0 * (1 - 0.00669342162296594323)) / ((1 - 0.00669342162296594323 * sin((lat) /180.0 * 3.1415926535897932384626) * sin((lat) /180.0 * 3.1415926535897932384626)) * (SQRT(1 - 0.00669342162296594323 * sin((lat) /180.0 * 3.1415926535897932384626) * sin((lat) /180.0 * 3.1415926535897932384626)))) * 3.1415926535897932384626))
               else lat end as lat
        ,longitude
        ,latitude
        ,freq
    from ods_5gdpi_step0);



cache table ods_5gdpi_step2 as
select
     t2.imsi
    ,t1.msisdn
    ,t2.gnbid
    ,t2.cellid
    ,starttime
    ,endtime
    ,t2.nrscssrsrp
    ,t2.nrscssrsrq
    ,t2.nrscsssinr
    ,lon
    ,lat
    ,t1.web_url
    ,t2.nrsctadv
    ,t2.nrngnbid
    ,t2.nrncellid
    ,t2.nrncssrsrp
    ,t2.nrncssrsrq
    ,t2.nrncsssinr
    ,t2.nrncarfcn
    ,t2.nrncpci
    ,t2.nrscarfcn
    ,t2.datetime
    ,t1.time1-t2.time2 as differencetime
    ,haoa
    ,vaoa
    ,nrscssbeamid
    ,t1.dis
    ,t1.freq
    ,case when nrsctadv is null and t1.freq='800M' and dis<=6000 then 1 when t1.freq = '800M' and abs(t2.nrsctadv*78.13-t1.dis)<=2000 then 1
when t1.freq = '2.1G' and abs(t2.nrsctadv*78.13-t1.dis)<=200 then 1
when t1.freq='3.5G' and abs(t2.nrsctadv*39.06-t1.dis)<=200 then 1

          else 0 end as is_valid          
    ,case when t1.freq in ('2.1G','800M') then  nrsctadv*78.13
          when t1.freq='3.5G' then  nrsctadv*39.06
          end as  dis1 
from
(
select * from ods_5gdpi_step1 where dis<3000
)t1
inner join
(select
    imsi
    ,nrsctadv
    ,gnbid
    ,cellid
    ,msisdn
    ,concat_ws(' ',split(datetime,'T')) as datetime
    ,unix_timestamp(concat_ws(' ',split(datetime,'T')),'yyyy-MM-dd HH:mm:ss.SSS') as time2
    ,(case when nrscssrsrp is not null then  (-156+nrscssrsrp)  else null end ) as nrscssrsrp
    ,(case when nrscssrsrq is not null then  (-43+nrscssrsrq/2) else null end ) as nrscssrsrq
    ,(case when nrscsssinr is not null then  (-23+nrscsssinr/2) else null end ) as nrscsssinr
    ,nrngnbid
    ,nrncellid
    ,nrncssrsrp
    ,nrncssrsrq
    ,nrncsssinr
    ,nrncarfcn
    ,nrncpci
    ,nrscarfcn
    ,haoa
    ,vaoa
    ,nrscssbeamid
from ods_nr_mro_northctcc_q
where  p_provincecode = 220000 and
    p_date = '2026-03-02' and
    p_hour = 5 and
msisdn is not null
)t2
on regexp_replace(t1.msisdn, '^86', '')=regexp_replace(t2.msisdn, '^86', '')
and concat(t1.nodebid,'_',t1.cellid)=concat(t2.gnbid,'_',t2.cellid)
where abs(time1-time2)/60<1;


insert overwrite table fact_5gdpi_5gmro_ott_h partition(
         p_provincecode = 220000,
    p_date = '2026-03-02',
    p_hour = 5
    )
    select
    imsi,
    msisdn,
    gnbid,
    cellid,
    starttime,
    endtime,
    nrscssrsrp,
    nrscssrsrq,
    nrscsssinr,
    lon,
    lat,
    web_url,
    nrsctadv,
    nrngnbid,
    nrncellid,
    nrncssrsrp,
    nrncssrsrq,
    nrncsssinr,
    nrncarfcn,
    nrncpci,
    nrscarfcn,
    `datetime`,
    differencetime,
    haoa,
    vaoa,
    nrscssbeamid,
    dis,
    freq,
    is_valid,
    dis1
from
    (
        select
            imsi,
            msisdn,
            gnbid,
            cellid,
            starttime,
            endtime,
            nrscssrsrp,
            nrscssrsrq,
            nrscsssinr,
            lon,
            lat,
            web_url,
            nrsctadv,
            nrngnbid,
            nrncellid,
            nrncssrsrp,
            nrncssrsrq,
            nrncsssinr,
            nrncarfcn,
            nrncpci,
            nrscarfcn,
            `datetime`,
            differencetime,
            haoa,
            vaoa,
            nrscssbeamid,
            dis,
            freq,
            is_valid,
            dis1,
            row_number() over (
                Partition by imsi,
                lon,
                lat,
                gnbid,
                cellid,
                starttime
                order by differencetime,abs(dis-dis1)
            ) as rank
        from ods_5gdpi_step2
         where
        is_valid=1
        and web_url!='delivery.yonghuivip.com'
)
where
    rank = 1;