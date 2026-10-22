# Cloud Infrastructure DNS Diagnostic Report
Generated: {{ timestamp }}
Domain: {{ domain }}
Resolver: {{ resolver }}

## Resource Records
- **A Records:** {{ a_records }}
- **AAAA Records:** {{ aaaa_records }}
- **MX Records:** {{ mx_records }}
- **TXT Records:** {{ txt_records }}
- **NS Records:** {{ ns_records }}

## Security Posture
- DNSSEC Validated: {{ dnssec_status }}
- Primary SOA Serial: {{ soa_serial }}
