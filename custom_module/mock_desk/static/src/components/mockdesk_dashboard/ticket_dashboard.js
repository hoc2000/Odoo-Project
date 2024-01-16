/** @odoo-module */

import { registry } from "@web/core/registry"
import { KpiCard } from "../kpi_card/kpi_card"
import { ChartRenderer } from "../chart_renderer/chart_renderer"
import { loadJS } from "@web/core/assets"
import { useService } from '@web/core/utils/hooks';
const { Component, onWillStart, useRef, onMounted, useState } = owl
//lấy color không bị trùng
import { getColor } from "@web/views/graph/colors"
//this will select the current web right now
var session = require('web.session');
//reload page
import { browser } from "@web/core/browser/browser"
import { routeToUrl } from "@web/core/browser/router_service"

export class OwlMockdeskDashboard extends Component {
    //Top Project (5 project limit)
    async getOpenTicketTeam() {
        let domain = [['is_closed', '=', false]]
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }
        const data = await this.orm.readGroup(this.model, domain, ['team_id'], ['team_id'], { limit: 5, orderby: "create_date desc" })
        const team_data = await this.orm.searchRead('mockdesk.teams', [], ['color'])
        // console.log(data)
        const color = ['#dadada', '#f06050', '#f4a460', '#f7cd1f', '#6cc1ed', '#814968', '#eb7b7f', '#2c8397', '#475577', '#d6145f', '#30c381', '#9365b8']

        this.state.openTicketTeam = {
            data: {
                labels: data.map(d => d.team_id[1]),
                datasets: [
                    {
                        label: 'Total Ticket',
                        data: data.map(d => d.team_id_count),
                        hoverOffset: 4,
                        backgroundColor: team_data.map(d => color[d.color]),

                    },

                ]
            }
        }
    }
    // Product of Project
    async GetFailedTicket() {
        let domain = [['is_failed', '=', true]]
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }
        const color = ['#dadada', '#f06050', '#f4a460', '#f7cd1f', '#6cc1ed', '#814968', '#eb7b7f', '#2c8397', '#475577', '#d6145f', '#30c381', '#9365b8']
        const data = await this.orm.readGroup('mockdesk.ticket', domain, ['team_id'], ['team_id'], { limit: 5, orderby: "create_date desc" })
        const team_data = await this.orm.searchRead('mockdesk.teams', [], ['color'])
        this.state.FailedTicket = {
            data: {
                labels: data.map(d => d.team_id[1]),
                datasets: [
                    {
                        label: 'Total Tickets',
                        data: data.map(d => d.team_id_count),
                        hoverOffset: 4,
                        backgroundColor: team_data.map(d => color[d.color]),
                    },

                ]
            }
        }
    }

    //Tassk by Status
    async getTicketbyStage() {
        let domain = []
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }
        const data = await this.orm.searchRead('mockdesk.teams', domain, ['name', 'ticket_new', 'ticket_inprogress', 'solved_ticket', 'cancelled_ticket'])
        // console.log(data)'
        this.state.ticketByStage = {
            data: {
                labels: data.map(d => d.name),
                datasets: [
                    {
                        label: 'New',
                        data: data.map(d => d.ticket_new),
                        hoverOffset: 4,
                        // backgroundColor: project_data.map(d => color[d.color]),
                    },
                    {
                        label: 'In Progress',
                        data: data.map(d => d.ticket_inprogress),
                        hoverOffset: 4,
                        // backgroundColor: project_data.map(d => color[d.color]),
                    },
                    {
                        label: 'Solved',
                        data: data.map(d => d.solved_ticket),
                        hoverOffset: 4,
                        // backgroundColor: project_data.map(d => color[d.color]),
                    },
                    {
                        label: 'Cancelled',
                        data: data.map(d => d.cancelled_ticket),
                        hoverOffset: 4,
                        // backgroundColor: project_data.map(d => color[d.color]),
                    },
                ]
            }
        }
    }
    // //Priority Tasks bar
    async getRatingTicket() {
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }
        const satisfied_count = await this.orm.searchCount('mockdesk.ticket', [['rating_avg', '=', 5]])
        const okay_count = await this.orm.searchCount('mockdesk.ticket', [['rating_avg', '=', 3]])
        const dissatisfied_count = await this.orm.searchCount('mockdesk.ticket', [['rating_avg', '=', 1]])
        // console.log(data)
        this.state.RatingValue = {
            data: {
                labels: [''],
                datasets: [
                    {
                        label: 'Satisfied',
                        data: [satisfied_count],
                        hoverOffset: 4,
                        backgroundColor: "#a9f451",
                    },
                    {
                        label: 'Okay',
                        data: [okay_count],
                        hoverOffset: 4,
                        backgroundColor: "#fcd382",
                    },
                    {
                        label: 'Dissatisfied',
                        data: [dissatisfied_count],
                        hoverOffset: 4,
                        backgroundColor: "#f56c6c",
                    },
                ],
            },
        }
    }


    //SET UP
    setup() {
        this.state = useState({
            uid: null,
            ticket: { value: 0, percentage: 0, },
            ticketList: [],
            openTicket: { value: 0, percentage: 0, },
            closedTicket: { value: 0, percentage: 0, },
            failedTicket: { value: 0, percentage: 0, },
            unassigedticket: { value: 0, percentage: 0, },
            period: 0,
        })
        this.model = "mockdesk.ticket"
        this.orm = useService("orm")
        this.actionService = useService("action")

        const old_chartjs = document.querySelector('script[src="/web/static/lib/Chart/Chart.js"]')
        const router = useService("router")

        if (old_chartjs) {
            let { search, hash } = router.current
            search.old_chartjs = old_chartjs != null ? "0" : "1"
            hash.action = 292
            browser.location.href = browser.location.origin + routeToUrl(router.current)
        }

        onWillStart(async () => {
            this.getDates()
            await this.GetAllTicket()
            await this.GetClosedTickets()
            await this.GetOpenTickets()
            await this.GetUnassignTicket()
            // //chart
            await this.getOpenTicketTeam()
            await this.GetFailedTicket()
            await this.getTicketbyStage()
            await this.getRatingTicket()
        })

    }
    //All tasks
    async GetAllTicket() {
        let domain = []
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }
        const countTicket = await this.orm.searchCount(this.model, domain)
        this.state.ticket.value = countTicket
    }

    viewTickets() {
        let domain = []
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "All Ticket",
            res_model: this.model,
            domain, //same name as domain so dont need to change add value
            views: [
                [false, "list"],
                [false, "kanban"],
                [false, "form"],
            ]
        })
    }


    // //Closed Ticket
    async GetClosedTickets() {
        //domain default can push though :))
        let domain = [['is_closed', '=', true]]
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }
        const closedTicket = await this.orm.searchCount(this.model, domain)
        this.state.closedTicket.value = closedTicket
    }


    viewClosedTickets() {
        let domain = [['is_closed', '=', true]]
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Closed Ticket",
            res_model: this.model,
            context: { "search_default_filter_closed_ticket": 1 },
            views: [
                [false, "list"],
                [false, "kanban"],
                [false, "form"],
            ]
        })
    }

    // //Open Ticket
    async GetOpenTickets() {
        //domain default can push though :))
        let domain = [['is_closed', '!=', true]]
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }
        const openTickets = await this.orm.searchCount(this.model, domain)
        this.state.openTicket.value = openTickets
    }

    viewOpenTickets() {
        let domain = [['is_closed', '!=', true]]
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Open Tickets",
            res_model: this.model,
            context: { "search_default_filter_open_ticket": 1 },
            views: [
                [false, "list"],
                [false, "kanban"],
                [false, "form"],
            ]
        })
    }
    // //Personal Tasks
    async GetUnassignTicket() {
        //domain default can push though :))
        // const uid = session.uid
        // this.state.uid = uid;
        let domain = [['assign_to', '=', false]]
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }
        const unassigedticket = await this.orm.searchCount(this.model, domain)
        // print(rateAvg)
        this.state.unassigedticket.value = unassigedticket
    }

    ViewUnassigedTicket() {
        let domain = [['assign_to', '=', false]]
        if (this.state.period > 0) {
            domain.push(['create_date', '>', this.state.date])
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Unassigned Ticket",
            res_model: this.model,
            context: { "search_default_unassign_filter": 1 },
            views: [
                [false, "list"],
                [false, "kanban"],
                [false, "form"],
            ]
        })
    }

    getDates() {
        this.state.date = moment().subtract(this.state.period, 'days').format('L');
    }

    async onChangePeriod() {
        //sử dụng mement của js

        this.getDates()
        await this.GetAllTicket()
        await this.GetClosedTickets()
        await this.GetOpenTickets()
        await this.GetUnassignTicket()
        // //chart
        await this.getOpenTicketTeam()
        await this.GetFailedTicket()
        await this.getTicketbyStage()
        await this.getRatingTicket()
    }
}

OwlMockdeskDashboard.template = "owl.MockdeskDashboard"
OwlMockdeskDashboard.components = { KpiCard, ChartRenderer }
registry.category("actions").add("owl.mockdesk_dashboard", OwlMockdeskDashboard)




