.echo on
CREATE INDEX MonthEndDayOfMonth on attacks(month,endDayOfMonth);
CREATE INDEX MonthDeviceIp on attacks(month,deviceIp);
CREATE INDEX MonthDestAddress on attacks(month,destAddress);
CREATE INDEX MonthName on attacks(month,name);
CREATE INDEX MonthGeoLocation on attacks(month,geoLocation);
CREATE INDEX MonthSourceAddress on attacks(month,sourceAddress);
CREATE INDEX MonthRulenamePktCount on attacks(month,ruleName,packetCount);
CREATE INDEX MonthRulenamePktBandwidth on attacks(month,ruleName,packetBandwidth);
CREATE INDEX MonthRuleName on attacks(month,ruleName);
CREATE INDEX MonthNamePktCount on attacks(month,name,packetCount);
CREATE INDEX MonthNamePktBandwidth on attacks(month,name,packetBandwidth);
CREATE INDEX MonthProtocolPort on attacks(month,protocolPort);
CREATE INDEX MonthProtocol on attacks(month,protocol);
CREATE INDEX MonthProtocolPktCount on attacks(month,protocol,packetCount);
CREATE INDEX MonthProtocolPktBandwidth on attacks(month,protocol,packetBandwidth);
CREATE INDEX MonthDurationRange on attacks(month,durationRange);
CREATE INDEX MonthCategoryPktCount on attacks(month,category,packetCount);
CREATE INDEX MonthCategoryPktBandwidth on attacks(month,category,packetBandwidth);
CREATE INDEX MonthYear on attacks(month,year);
CREATE INDEX MonthYearPktCount on attacks(month,year,packetCount);
CREATE INDEX MonthYearPktBandwidth on attacks(month,year,packetBandwidth);
.quit
