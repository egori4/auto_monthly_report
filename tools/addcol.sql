.echo on
alter table attacks add column averageAttackPacketRatePps INTEGER;
alter table attacks add column maxAttackPacketRatePps INTEGER;
alter table attacks add column averageAttackRateBps INTEGER;
alter table attacks add column maxAttackRateBps INTEGER;
.quit
