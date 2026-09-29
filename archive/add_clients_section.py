#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add CLIENTS section to dashboard.html"""

with open('rcagents_saas_core/frontend/templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

marker = '<!-- ====== END CUSTOMERS ====== -->'
pos = content.find(marker)
if pos < 0:
    print("ERROR: marker not found!")
    exit(1)

clients_section = """
            <!-- ====== CLIENTS ====== -->
            <div x-show=\"view === 'clients'\" x-data=\"{ clientSearch: '' }\">
                <div class=\"flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 gap-3\">
                    <div>
                        <h2 class=\"text-lg font-bold text-white flex items-center gap-2\"><i class=\"fa-solid fa-users text-neon-purple\"></i> Clients</h2>
                        <p class=\"text-xs text-gray-500 font-mono mt-1\" x-text=\"clients.length + ' clients | DZD ' + Number(clients.reduce((a,b)=>a+(b.spent||0),0)).toLocaleString() + ' total revenue'\"></p>
                    </div>
                    <div class=\"relative w-full sm:w-64\">
                        <i class=\"fa-solid fa-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-xs\"></i>
                        <input type=\"text\" x-model=\"clientSearch\" placeholder=\"Search by name, phone, wilaya...\" class=\"w-full bg-rc-bg border border-rc-border/50 rounded-lg pl-9 pr-3 py-2 text-xs text-gray-200 font-mono placeholder-gray-600 focus:outline-none focus:border-neon-purple/50 transition-colors\">
                    </div>
                </div>

                <!-- Loading -->
                <div x-show=\"loading\" class=\"py-10 text-center\">
                    <div class=\"inline-flex items-center gap-3 text-gray-500\">
                        <i class=\"fa-solid fa-circle-notch text-neon-purple text-xl animate-spin\"></i>
                        <span class=\"text-sm font-mono tracking-wider\">LOADING CLIENTS...</span>
                    </div>
                </div>

                <template x-if=\"!loading && clients.length === 0\">
                    <div class=\"bg-rc-card border border-rc-border/60 rounded-xl p-8 text-center\">
                        <i class=\"fa-solid fa-users text-4xl text-gray-600 mb-4\"></i>
                        <h3 class=\"text-sm font-semibold text-gray-400\">No clients yet</h3>
                        <p class=\"text-xs text-gray-500 mt-1\">Client data will appear once orders start coming in.</p>
                    </div>
                </template>

                <template x-if=\"!loading && clients.length > 0\">
                    <div class=\"bg-rc-card border border-rc-border/60 rounded-xl overflow-hidden card-hover-glow\">
                        <div class=\"overflow-x-auto\">
                            <table class=\"w-full text-xs\">
                                <thead>
                                    <tr class=\"text-gray-500 font-mono text-[10px] border-b border-rc-border/40 bg-rc-card-hover/30\">
                                        <th class=\"text-left py-3 px-4 font-medium\">Client</th>
                                        <th class=\"text-left py-3 px-4 font-medium\">Phone</th>
                                        <th class=\"text-left py-3 px-4 font-medium\">Wilaya</th>
                                        <th class=\"text-left py-3 px-4 font-medium\">Municipality</th>
                                        <th class=\"text-center py-3 px-4 font-medium\">Orders</th>
                                        <th class=\"text-right py-3 px-4 font-medium\">Total Spent</th>
                                        <th class=\"text-right py-3 px-4 font-medium\">Last Order</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <template x-for=\"c in clients.filter(x => {
                                        if (!clientSearch) return true;
                                        const q = clientSearch.toLowerCase();
                                        return (x.name||'').toLowerCase().includes(q) ||
                                               (x.phone||'').toLowerCase().includes(q) ||
                                               (x.wilaya||'').toLowerCase().includes(q);
                                    })\" :key=\"c.id\">
                                        <tr class=\"border-b border-rc-border/20 hover:bg-rc-card-hover/30 transition-colors\">
                                            <td class=\"py-3.5 px-4\">
                                                <div class=\"flex items-center gap-2.5\">
                                                    <div class=\"w-8 h-8 rounded-lg bg-gradient-to-br from-neon-purple/10 to-neon-pink/10 border border-neon-purple/20 flex items-center justify-center text-xs font-bold text-neon-purple\" x-text=\"(c.name||'?')[0]\"></div>
                                                    <div>
                                                        <p class=\"text-xs font-medium text-gray-200\" x-text=\"c.name || 'Unknown'\"></p>
                                                    </div>
                                                </div>
                                            </td>
                                            <td class=\"py-3.5 px-4\">
                                                <span class=\"text-xs font-mono text-gray-400\" x-text=\"c.phone || '---'\"></span>
                                            </td>
                                            <td class=\"py-3.5 px-4\">
                                                <span class=\"text-xs text-gray-400\" x-text=\"c.wilaya || '---'\"></span>
                                            </td>
                                            <td class=\"py-3.5 px-4\">
                                                <span class=\"text-xs text-gray-500\" x-text=\"c.municipality || '---'\"></span>
                                            </td>
                                            <td class=\"py-3.5 px-4 text-center\">
                                                <span class=\"text-sm font-bold font-mono text-white\" x-text=\"c.orders || 0\"></span>
                                            </td>
                                            <td class=\"py-3.5 px-4 text-right\">
                                                <span class=\"text-xs font-bold font-mono text-neon-cyan\" x-text=\"Number(c.spent||0).toLocaleString() + ' DZD'\"></span>
                                            </td>
                                            <td class=\"py-3.5 px-4 text-right\">
                                                <span class=\"text-[10px] font-mono text-gray-500\" x-text=\"c.last_order ? new Date(c.last_order).toLocaleDateString('fr-DZ', {day:'2-digit', month:'short', year:'numeric'}) : '---'\"></span>
                                            </td>
                                        </tr>
                                    </template>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </template>
            </div>

"""

before = content[:pos + len(marker)]
after = content[pos + len(marker):]
new_content = before + clients_section + after

with open('rcagents_saas_core/frontend/templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Done! Added CLIENTS section successfully.")
