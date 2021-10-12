-- setup
drop table if exists sock_proto;
create table sock_proto (id INTEGER, name TEXT);
insert into sock_proto (id, name) values
    (0, 'HOPOPT'), -- IPv6 Hop-by-Hop Option
    (1, 'ICMP'), -- Internet Control Message Protocol
    (2, 'IGMP'), -- Internet Group Management Protocol
    (4, 'IPv4-in-IP'), -- IPv4 encapsulation
    (6, 'TCP'), -- Transmission Control Protocol
    (8, 'EGP'), -- Exterior Gateway Protocol
    (9, 'IGP'), -- Interior Gateway Protocol (used by Cisco for their IGRP)
    (16, 'CHAOS'), -- Chaos
    (17, 'UDP'), -- User Datagram Protocol
    (33, 'DCCP'), -- Datagram Congestion Control Protocol
    (37, 'DDP'), -- Datagram Delivery Protocol
    (41, 'IPv6-in-IP'), -- IPv6 Encapsulation
    (46, 'RSVP'), -- Resource Reservation Protocol
    (47, 'GRE'), -- Generic Routing Encapsulation
    (48, 'DSR'), -- Dynamic Source Routing Protocol
    (50, 'ESP'), -- Encapsulating Security Payload
    (51, 'AH'), -- Authentication Header
    (55, 'MOBILE'), -- IP Mobility (Min Encap)
    (58, 'IPv6-ICMP'), -- Internet Control Message (IPv6)
    (59, 'IPv6-NoNxt'), -- No Next Header for IPv6
    (60, 'IPv6-Opts'), -- Destination Options for IPv6
    (84, 'TTP'), -- TTP
    (88, 'EIGRP'), -- EIGRP
    (89, 'OSPF'), -- Open Shortest Path First
    (93, 'AX.25'), -- AX.25
    (103, 'PIM'), -- Protocol Independent Multicast
    (105, 'SCPS'), -- SCPS (Space Communications Protocol Standards)
    (108, 'IPComp'), -- IP Payload Compression Protocol
    (112, 'VRRP'), -- Virtual Router Redundancy Protocol, Common Address Redundancy Protocol (not IANA assigned)
    (113, 'PGM'), -- PGM Reliable Transport Protocol
    (115, 'L2TP'), -- Layer Two Tunneling Protocol Version 3
    (124, 'IS-IS over IPv4'), -- Intermediate System to Intermediate System (IS-IS) Protocol over IPv4
    (132, 'SCTP'), -- Stream Control Transmission Protocol
    (133, 'FC'), -- Fibre Channel
    (136, 'UDPLite'), -- Lightweight User Datagram Protocol
    (137, 'MPLS-in-IP'), -- Multiprotocol Label Switching Encapsulated in IP
    (138, 'manet'), -- MANET Protocols
    (139, 'HIP'), -- Host Identity Protocol
    (140, 'Shim6'), -- Site Multihoming by IPv6 Intermediation
    (142, 'ROHC') -- Robust Header Compression
;

drop table if exists sock_family;
create table sock_family (id INTEGER, name TEXT);
insert into sock_family (id, name) values
    ('AF_UNSPEC', 0),
    ('AF_UNIX', 1), -- Unix domain sockets
    ('AF_INET', 2), -- Internet IP Protocol
    ('AF_AX25', 3), -- Amateur Radio AX.25
    ('AF_IPX', 4), -- Novell IPX
    ('AF_APPLETALK', 5), -- Appletalk DDP
    ('AF_NETROM', 6), -- Amateur radio NetROM
    ('AF_BRIDGE', 7), -- Multiprotocol bridge
    ('AF_AAL5', 8), -- Reserved for Werner's ATM
    ('AF_X25', 9), -- Reserved for X.25 project
    ('AF_INET6', 10), -- IP version 6
    ('AF_MAX', 12) -- For now..
;

-- listening ports
select
    p.pid,
    p.name,
    p.path,
    p.on_disk,
    coalesce((select name from sock_proto where id = lp.protocol), lp.protocol) proto,
    coalesce((select name from sock_family where id = lp.family), lp.family) family,
    lp.address,
    lp.port
from listening_ports lp
join processes p on lp.pid = p.pid
where lp.port != 0;

-- open sockets
select
    p.pid,
    p.name,
    p.path,
    p.on_disk,
    coalesce((select name from sock_proto where id = pos.protocol), pos.protocol) proto,
    coalesce((select name from sock_family where id = pos.family), pos.family) family,
    pos.local_address,
    pos.local_port,
    pos.remote_address,
    pos.remote_port,
    pos.state,
    pos.net_namespace
from process_open_sockets pos
join processes p on pos.pid = p.pid
where (pos.local_port != 0 or pos.remote_port != 0) and pos.local_port = 22;

-- opened files
select
    p.pid,
    p.name,
    p.path process_path,
    pof.path file_path
from process_open_files pof
join processes p on pof.pid = p.pid
where
    pof.path like '/home/siikamiika/.cache/%';

-- firefox extensions
select
    fa.identifier,
    fa.version
from firefox_addons fa
join users u on fa.uid = u.uid
where
    u.username = 'siikamiika'
    and fa.type = 'extension';
