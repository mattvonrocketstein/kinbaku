""" kinbaku.codebase.search
      mixin for codebase
"""

class Search(object):
    def _search(self, name):
        """  internal search method
               NOTE: example_rules = {'s': {'type': '__builtins__.str','unsure': True}})
        """
        def get_matches(sections):
            """ obtain match objections inside sections """
            matches  = []
            for diff_marker, line in sections:
                junk1, data1,data2, junk2 = diff_marker.split()
                lineno  = data1.replace('-','').split(',')[0]
                lineno  = int(lineno)
                lineno += 3
                match   = dict( real_path = real_path,   # actually it's pth_shadow-relative
                                line=line[1:],           # snips off the "-" from the diff
                                lineno=lineno, )         # fully adjusted.
                matches.append(match)
            return matches

        pattern, goal, rules = name, '', {}

        ## Mirror code-files-only into the sandbox
        self.snapshot()

        ## Setup and grab data from rope-restructuring
        #strukt  = restructure.Restructure(self.project, pattern, goal, rules)
        #changes = strukt.get_changes()
        #strukt  = self.restructure(pattern,goal,rules)
        changes = self.get_changes(pattern,goal,rules)


        descr   = changes.description
        out     = dict( pattern=pattern, goal=goal, rules=rules,
                        descr=descr, changes=changes,)

        ## Build match-dictionaries with line numbers, etc
        real_changes  = changes.changes
        if real_changes:
            change_map = []
            for change_contents in real_changes:
                real_path  = change_contents.resource.real_path
                name       = path(real_path).name
                udiff      = change_contents.get_description().split('\n')

                do_test = lambda line: \
                          line.startswith('@@') or \
                          (line.startswith('-') and \
                           not line.startswith('---'))
                mdiff   = [ line for line in udiff if do_test(line) ]

                if len(mdiff) %2 != 0:
                    raise ValueError, "expected mdiff would be divisible by two."

                sections = groupby(mdiff, 2)
                matches  = get_matches(sections)
                result   = dict( real_path = real_path,
                                 name      = name,
                                 matches   = matches,
                                 diff      = udiff, )
                change_map.append(result)
            out.update(change_map=change_map)

        out.update(dict(moved = changes.get_changed_resources()))
        return out
