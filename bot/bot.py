import sc2
from sc2 import BotAI, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2
from sc2.player import Bot, Computer


class CompetitiveBot(BotAI):
    NAME: str = "goomibot"

    RACE: Race = Race.Protoss
    """This bot's Starcraft 2 race.
    Options are:
        Race.Terran
        Race.Zerg
        Race.Protoss
        Race.Random
    """

    def __init__(self):
        # Initialize inherited class
        sc2.BotAI.__init__(self)

    async def on_start(self):
        print("Game start")
        # Do things here before the game starts

    async def on_step(self, iteration):
        # Populate this function with whatever your bot should do!
        if iteration == 0:
            await self.chat_send("GLHF")
        
        await self.distribute_workers()
        await self.build_supply()
        await self.build_workers()

        await self.build_gateway()
        await self.build_gas()
        await self.build_cybernetic()
        await self.train_stalkers()
        if self.structures(UnitTypeId.CYBERNETICSCORE).ready:
            await self.rsrch_warpgate()
            await self.build_four_gw()
        await self.chrono_boost()

        if self.time > 400:
            print(self.time)
            self.chat_send("GG")
            self.leave()
    
    async def build_workers(self):
        main = self.townhalls.ready.random
        if ( self.can_afford(UnitTypeId.PROBE) and 
                main.is_idle and 
                self.workers.amount < self.townhalls.amount*20 ):
            main.train(UnitTypeId.PROBE)
    
    async def build_supply(self):
        if ( self.supply_left < 3 and 
                not self.already_pending(UnitTypeId.PYLON) and 
                self.can_afford(UnitTypeId.PYLON) ):
            if self.structures(UnitTypeId.PYLON).amount < 1:
                await self.build(UnitTypeId.PYLON, near=list(self.main_base_ramp.upper)[0])
            if self.structures(UnitTypeId.PYLON).amount > 3:
                await self.build(UnitTypeId.PYLON, near=self.townhalls.ready.random.position.towards(list(self.main_base_ramp.upper)[0], -10))
            else:
                await self.build(UnitTypeId.PYLON, near=self.townhalls.ready.random.position.towards(list(self.main_base_ramp.upper)[0], 5))
    
    async def build_gateway(self):
        if ( self.structures(UnitTypeId.PYLON).ready and
                self.can_afford(UnitTypeId.GATEWAY) and
                not self.structures(UnitTypeId.GATEWAY) ):
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.GATEWAY, near=pylon)
    
    async def build_gas(self):
        if self.structures(UnitTypeId.GATEWAY):
            for main in self.townhalls.ready:
                for gas in self.vespene_geyser.closer_than(15, main):
                    if not self.can_afford(UnitTypeId.ASSIMILATOR):
                        break
                    wrkr = self.select_build_worker(gas.position)
                    if wrkr is None:
                        break
                    if not self.gas_buildings or not self.gas_buildings.closer_than(1, gas):
                        wrkr.build(UnitTypeId.ASSIMILATOR, gas)
                        wrkr.stop(queue=True)

    async def build_cybernetic(self):
        if self.structures(UnitTypeId.PYLON).ready:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            if self.structures(UnitTypeId.GATEWAY).ready:
                # if no cybernetics, then build one
                if not self.structures(UnitTypeId.CYBERNETICSCORE):
                    if ( self.can_afford(UnitTypeId.CYBERNETICSCORE) and
                            self.already_pending(UnitTypeId.CYBERNETICSCORE) == 0 ):
                        await self.build(UnitTypeId.CYBERNETICSCORE, near=pylon.position.towards(self.townhalls.ready.random, 10))
    
    async def build_four_gw(self):
        if ( self.structures(UnitTypeId.PYLON).ready and
                self.can_afford(UnitTypeId.GATEWAY) and
                self.structures(UnitTypeId.GATEWAY).amount + self.structures(UnitTypeId.WARPGATE).amount < 4 ):
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.GATEWAY, near=pylon)
        if ( self.structures(UnitTypeId.PYLON).ready and
                self.can_afford(UnitTypeId.GATEWAY) and
                self.structures(UnitTypeId.GATEWAY).amount + self.structures(UnitTypeId.WARPGATE).amount < 4 ):
            await self.build(UnitTypeId.GATEWAY, near=pylon)
        if ( self.structures(UnitTypeId.PYLON).ready and
                self.can_afford(UnitTypeId.GATEWAY) and
                self.structures(UnitTypeId.GATEWAY).amount + self.structures(UnitTypeId.WARPGATE).amount < 4 ):
            await self.build(UnitTypeId.GATEWAY, near=pylon)

    async def chrono_boost(self):
        if self.structures(UnitTypeId.PYLON):
            main = self.townhalls.ready.random
            if ( not main.is_idle ):
                main(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, main)
    
    async def rsrch_warpgate(self):
        if ( self.can_afford(AbilityId.RESEARCH_WARPGATE) and
                self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) == 0 ):
            cybercore = self.structures(UnitTypeId.CYBERNETICSCORE).ready.first
            cybercore.research(UpgradeId.WARPGATERESEARCH)


    async def train_stalkers(self):
        for gateway in self.structures(UnitTypeId.GATEWAY).ready:
            if ( self.can_afford(UnitTypeId.STALKER) and
                    gateway.is_idle ):
                gateway.train(UnitTypeId.STALKER)
                # unit.move(self.main_base_ramp.bottom_center)
    
    async def attack(self):
        stalkers = self.units(UnitTypeId.STALKER).ready.idle

        for stalker in stalkers:
            if self.units(UnitTypeId.STALKER).amount > 5:
                stalker.attack(self.enemy_start_location[0])


    def on_end(self, result):
        print("Game finish", result)
        # Do things here after the game ends
