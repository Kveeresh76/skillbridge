import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, MapPin, Search, Sparkles, X } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function Discover() {
  const { user } = useAuth();
  const [people, setPeople] = useState([]);
  const [skills, setSkills] = useState([]);
  const [mySkills, setMySkills] = useState([]);
  const [categories, setCategories] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedPerson, setSelectedPerson] = useState(null);
  const [teachingSkill, setTeachingSkill] = useState('');
  const [learningSkill, setLearningSkill] = useState('');
  const [message, setMessage] = useState('');
  const [requestError, setRequestError] = useState('');
  const [requestSent, setRequestSent] = useState(false);
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    Promise.all([api.get('/discover/people'), api.get('/discover/categories'), api.get('/discover/skills'), api.get('/workspace/profile')])
      .then(([peopleResponse, categoriesResponse, skillsResponse, profileResponse]) => {
        setPeople(peopleResponse.data.people);
        setCategories(categoriesResponse.data.categories);
        setSkills(skillsResponse.data.skills);
        setMySkills(profileResponse.data.skills);
      })
      .catch(() => setError('We could not load the community right now. Please refresh and try again.'))
      .finally(() => setIsLoading(false));
  }, []);

  const filteredPeople = useMemo(() => {
    const term = search.trim().toLowerCase();
    return people.filter((person) => {
      const matchesCategory = selectedCategory === 'All' || person.offered_skills.some((skill) => skill.category === selectedCategory);
      const matchesSearch = !term || person.full_name.toLowerCase().includes(term) || person.offered_skills.some((skill) => skill.name.toLowerCase().includes(term));
      return matchesCategory && matchesSearch;
    });
  }, [people, search, selectedCategory]);

  const teachingOptions = mySkills
    .filter((skill) => skill.type === 'OFFERED')
    .map((skill) => ({ name: skill.name }));

  function openRequest(person) {
    setSelectedPerson(person);
    setTeachingSkill('');
    setLearningSkill('');
    setMessage(`Hi ${person.full_name.split(' ')[0]}, I would love to exchange skills with you.`);
    setRequestError('');
    setRequestSent(false);
  }

  async function submitRequest(event) {
    event.preventDefault();
    setRequestError('');
    setIsSending(true);
    const teaching = skills.find((skill) => skill.name === teachingSkill);
    const learning = skills.find((skill) => skill.name === learningSkill);
    try {
      await api.post('/requests', {
        receiver_id: selectedPerson.id,
        teaching_skill_id: teaching.id,
        learning_skill_id: learning.id,
        message,
      });
      setRequestSent(true);
    } catch (request) {
      setRequestError(request.response?.data?.detail || 'The request could not be sent. Please try again.');
    } finally {
      setIsSending(false);
    }
  }

  return (
    <main className="min-h-screen bg-surface-light dark:bg-surface-dark">
      <header className="border-b border-ink-100 bg-white dark:border-ink-800 dark:bg-ink-950">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
          <Link to="/" className="font-display text-xl font-semibold text-ink-900 dark:text-ink-50">SkillBridge</Link>
          <Link to="/dashboard" className="btn-secondary"><ArrowLeft className="h-4 w-4" /> Dashboard</Link>
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-6 py-10 sm:py-14">
        <section className="max-w-2xl">
          <p className="text-sm font-medium uppercase tracking-[0.16em] text-ember-600">The skill exchange</p>
          <h1 className="mt-3 font-display text-4xl text-ink-900 dark:text-ink-50 sm:text-5xl">Find someone worth learning from.</h1>
          <p className="mt-4 text-ink-500 dark:text-ink-300">Browse people by what they can teach, then start a conversation around a useful exchange.</p>
        </section>

        <section className="mt-8 flex flex-col gap-4 sm:flex-row">
          <label className="relative block flex-1">
            <span className="sr-only">Search skills or people</span>
            <Search className="pointer-events-none absolute left-3 top-3 h-5 w-5 text-ink-400" aria-hidden="true" />
            <input className="input-field h-11 pl-10" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search skills or people" />
          </label>
        </section>

        <div className="mt-5 flex gap-2 overflow-x-auto pb-2">
          {['All', ...categories].map((category) => (
            <button key={category} className={`shrink-0 rounded-full px-4 py-2 text-sm transition-colors ${selectedCategory === category ? 'bg-ink-900 text-white dark:bg-ember-500' : 'bg-white text-ink-600 hover:bg-ink-100 dark:bg-ink-900 dark:text-ink-200 dark:hover:bg-ink-800'}`} onClick={() => setSelectedCategory(category)} type="button">
              {category}
            </button>
          ))}
        </div>

        {error && <p className="mt-8 text-sm text-red-700" role="alert">{error}</p>}
        {isLoading && <p className="mt-10 text-sm text-ink-500">Loading the community...</p>}
        {!isLoading && !error && <p className="mt-8 text-sm text-ink-500 dark:text-ink-300">{filteredPeople.length} people sharing their skills</p>}

        {!isLoading && !error && filteredPeople.length === 0 && <div className="card mt-4 p-10 text-center text-ink-500">No people match that search yet.</div>}
        <section className="mt-4 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {filteredPeople.map((person) => (
            <article className="card flex flex-col p-6" key={person.id}>
              <div className="flex items-start gap-3">
                <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-ember-100 font-display text-xl text-ember-800">{person.full_name.charAt(0)}</span>
                <div className="min-w-0">
                  <h2 className="truncate font-display text-xl text-ink-900 dark:text-ink-50">{person.full_name}</h2>
                  <p className="text-sm text-ink-500 dark:text-ink-300">{person.experience_level || 'SkillBridge member'}</p>
                </div>
              </div>
              {person.location && <p className="mt-4 flex items-center gap-1 text-xs text-ink-400"><MapPin className="h-3.5 w-3.5" /> {person.location}</p>}
              <p className="mt-4 line-clamp-2 min-h-10 text-sm text-ink-500 dark:text-ink-300">{person.bio || 'Ready to exchange knowledge with the community.'}</p>
              <div className="mt-5">
                <p className="text-xs font-medium uppercase tracking-wider text-ink-400">Can teach</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {person.offered_skills.map((skill) => <span className="rounded-full bg-ink-100 px-2.5 py-1 text-xs text-ink-700 dark:bg-ink-800 dark:text-ink-200" key={skill.name}>{skill.name}</span>)}
                </div>
              </div>
              <div className="mt-5 border-t border-ink-100 pt-4 dark:border-ink-800">
                <p className="flex items-center gap-1 text-xs text-ink-400"><Sparkles className="h-3.5 w-3.5 text-ember-500" /> Wants to learn {person.wanted_skills.slice(0, 2).join(' and ') || 'new skills'}</p>
              </div>
              <button className="btn-primary mt-5 w-full" type="button" onClick={() => openRequest(person)}>Start an exchange</button>
            </article>
          ))}
        </section>
      </div>

      {selectedPerson && <div className="fixed inset-0 z-10 flex items-center justify-center bg-ink-950/50 px-6 py-8" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setSelectedPerson(null); }}>
        <section className="card w-full max-w-lg p-6 sm:p-8" role="dialog" aria-modal="true" aria-labelledby="exchange-title">
          <div className="flex items-start justify-between gap-4">
            <div><p className="text-sm text-ember-600">New exchange request</p><h2 id="exchange-title" className="mt-1 font-display text-2xl text-ink-900 dark:text-ink-50">Connect with {selectedPerson.full_name}</h2></div>
            <button className="rounded-md p-1 text-ink-400 hover:bg-ink-100 hover:text-ink-900 dark:hover:bg-ink-800" type="button" onClick={() => setSelectedPerson(null)} aria-label="Close exchange form"><X className="h-5 w-5" /></button>
          </div>
          {requestSent ? <div className="mt-8 rounded-md border border-green-200 bg-green-50 p-4 text-sm text-green-800">Your exchange request was sent to {selectedPerson.full_name}. <button className="ml-1 font-medium underline" type="button" onClick={() => setSelectedPerson(null)}>Close</button></div> : <form className="mt-7 space-y-5" onSubmit={submitRequest}>
            {!user && <p className="rounded-md bg-ember-50 p-3 text-sm text-ember-800">Please sign in before sending an exchange request.</p>}
            <label className="block text-sm font-medium text-ink-800 dark:text-ink-100">I can teach
              <select className="input-field mt-2" value={teachingSkill} onChange={(event) => setTeachingSkill(event.target.value)} required disabled={!user}>
                <option value="">Choose one of your offered skills</option>
                {teachingOptions.map((skill) => <option key={skill.name} value={skill.name}>{skill.name}</option>)}
              </select>
            </label>
            <label className="block text-sm font-medium text-ink-800 dark:text-ink-100">I want to learn
              <select className="input-field mt-2" value={learningSkill} onChange={(event) => setLearningSkill(event.target.value)} required disabled={!user}>
                <option value="">Choose a skill</option>
                {selectedPerson.offered_skills.map((skill) => <option key={skill.name} value={skill.name}>{skill.name}</option>)}
              </select>
            </label>
            <label className="block text-sm font-medium text-ink-800 dark:text-ink-100">Message
              <textarea className="input-field mt-2 min-h-24 resize-y" value={message} onChange={(event) => setMessage(event.target.value)} required maxLength={500} disabled={!user} />
            </label>
            {teachingOptions.length === 0 && user && <p className="text-sm text-ember-700">Add an offered skill to your profile before sending a request.</p>}
            {requestError && <p className="text-sm text-red-700" role="alert">{requestError}</p>}
            <button className="btn-primary w-full" type="submit" disabled={!user || !teachingOptions.length || isSending}>{isSending ? 'Sending request...' : 'Send exchange request'}</button>
          </form>}
        </section>
      </div>}
    </main>
  );
}
